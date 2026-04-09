"""Tests for hardening features: request_id, to_list, with_options, custom http_client,
idempotency, and with_raw_response."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel

from listbee import DefaultAsyncHttpxClient, DefaultHttpxClient, ListBee
from listbee._base_client import AsyncClient, SyncClient
from listbee._exceptions import APIStatusError, NotFoundError, RateLimitError, raise_for_status
from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee._raw_response import RawResponse
from listbee.types.account import AccountResponse

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_account_dict() -> dict:
    return {
        "object": "account",
        "id": "acc_test",
        "email": "test@example.com",
        "plan": "free",
        "fee_rate": "0.10",
        "billing_status": "active",
        "display_name": "Test",
        "bio": None,
        "ga_measurement_id": None,
        "notify_orders": True,
        "readiness": {
            "operational": False,
            "actions": [],
            "next": None,
        },
        "stats": {
            "total_revenue": 0,
            "total_orders": 0,
            "total_listings": 0,
        },
        "created_at": "2024-01-01T00:00:00Z",
    }


def _error_body(**overrides) -> dict:
    base = {
        "type": "https://docs.listbee.so/errors/not-found",
        "title": "Not Found",
        "status": 404,
        "detail": "Resource not found",
        "code": "not_found",
    }
    base.update(overrides)
    return base


class FakeItem(BaseModel):
    name: str


# ---------------------------------------------------------------------------
# 1. request_id on errors
# ---------------------------------------------------------------------------


class TestRequestIdOnErrors:
    def test_request_id_populated_from_header(self):
        headers = {"x-request-id": "req_abc123"}
        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(404, _error_body(), headers)
        assert exc_info.value.request_id == "req_abc123"

    def test_request_id_is_none_when_header_absent(self):
        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(404, _error_body(), {})
        assert exc_info.value.request_id is None

    def test_request_id_on_rate_limit_error(self):
        headers = {
            "x-request-id": "req_ratelimit",
            "x-ratelimit-limit": "60",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1711612800",
        }
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(429, _error_body(status=429, code="rate_limited"), headers)
        assert exc_info.value.request_id == "req_ratelimit"

    def test_request_id_on_explicit_construction(self):
        err = APIStatusError(
            type="https://docs.listbee.so/errors/not-found",
            title="Not Found",
            status=404,
            detail="Not found",
            code="not_found",
            request_id="req_explicit",
        )
        assert err.request_id == "req_explicit"


# ---------------------------------------------------------------------------
# 2. Pagination .to_list()
# ---------------------------------------------------------------------------


class TestToList:
    def _make_page(
        self, names: list[str], has_more: bool = False, cursor: str | None = None
    ) -> SyncCursorPage[FakeItem]:
        return SyncCursorPage(
            data=[FakeItem(name=n) for n in names],
            has_more=has_more,
            total_count=len(names),
            cursor=cursor,
            client=MagicMock(),
            path="/test",
            params={},
            model=FakeItem,
        )

    def test_to_list_single_page(self):
        page = self._make_page(["a", "b", "c"])
        result = page.to_list()
        assert [i.name for i in result] == ["a", "b", "c"]

    def test_to_list_respects_limit(self):
        page = self._make_page(["a", "b", "c"])
        result = page.to_list(limit=2)
        assert [i.name for i in result] == ["a", "b"]

    def test_to_list_limit_larger_than_page(self):
        page = self._make_page(["a", "b"])
        result = page.to_list(limit=10)
        assert [i.name for i in result] == ["a", "b"]

    def test_to_list_multi_page(self):
        mock_client = MagicMock()
        page2 = SyncCursorPage(
            data=[FakeItem(name="c")],
            has_more=False,
            total_count=1,
            cursor=None,
            client=mock_client,
            path="/test",
            params={},
            model=FakeItem,
        )
        mock_client.get_page.return_value = page2

        page1 = SyncCursorPage(
            data=[FakeItem(name="a"), FakeItem(name="b")],
            has_more=True,
            total_count=3,
            cursor="cur_next",
            client=mock_client,
            path="/test",
            params={},
            model=FakeItem,
        )
        result = page1.to_list()
        assert [i.name for i in result] == ["a", "b", "c"]

    def test_to_list_limit_stops_mid_multi_page(self):
        mock_client = MagicMock()
        page2 = SyncCursorPage(
            data=[FakeItem(name="c"), FakeItem(name="d")],
            has_more=False,
            total_count=2,
            cursor=None,
            client=mock_client,
            path="/test",
            params={},
            model=FakeItem,
        )
        mock_client.get_page.return_value = page2

        page1 = SyncCursorPage(
            data=[FakeItem(name="a"), FakeItem(name="b")],
            has_more=True,
            total_count=4,
            cursor="cur_next",
            client=mock_client,
            path="/test",
            params={},
            model=FakeItem,
        )
        result = page1.to_list(limit=3)
        assert [i.name for i in result] == ["a", "b", "c"]

    def test_to_list_empty(self):
        page = self._make_page([])
        assert page.to_list() == []


class TestAsyncToList:
    def _make_page(self, names: list[str]) -> AsyncCursorPage[FakeItem]:
        mock_client = AsyncMock()
        return AsyncCursorPage(
            data=[FakeItem(name=n) for n in names],
            has_more=False,
            total_count=len(names),
            cursor=None,
            client=mock_client,
            path="/test",
            params={},
            model=FakeItem,
        )

    def test_async_to_list(self):
        page = self._make_page(["x", "y"])

        async def run():
            return await page.to_list()

        result = asyncio.get_event_loop().run_until_complete(run())
        assert [i.name for i in result] == ["x", "y"]

    def test_async_to_list_with_limit(self):
        page = self._make_page(["x", "y", "z"])

        async def run():
            return await page.to_list(limit=2)

        result = asyncio.get_event_loop().run_until_complete(run())
        assert [i.name for i in result] == ["x", "y"]


# ---------------------------------------------------------------------------
# 3. with_options()
# ---------------------------------------------------------------------------


class TestWithOptions:
    def test_with_options_overrides_api_key(self):
        client = ListBee(api_key="lb_original")
        new_client = client.with_options(api_key="lb_override")
        assert new_client._api_key == "lb_override"
        assert client._api_key == "lb_original"  # original unchanged

    def test_with_options_overrides_timeout(self):
        client = ListBee(api_key="lb_test", timeout=30.0)
        new_client = client.with_options(timeout=5.0)
        assert new_client._timeout == 5.0
        assert client._timeout == 30.0

    def test_with_options_overrides_max_retries(self):
        client = ListBee(api_key="lb_test", max_retries=3)
        new_client = client.with_options(max_retries=0)
        assert new_client._max_retries == 0
        assert client._max_retries == 3

    def test_with_options_preserves_base_url(self):
        client = ListBee(api_key="lb_test", base_url="https://custom.api.example.com")
        new_client = client.with_options(timeout=1.0)
        assert new_client._base_url == "https://custom.api.example.com"

    def test_with_options_inherits_api_key_when_not_provided(self):
        client = ListBee(api_key="lb_inherited")
        new_client = client.with_options(timeout=10.0)
        assert new_client._api_key == "lb_inherited"

    def test_with_options_returns_new_instance(self):
        client = ListBee(api_key="lb_test")
        new_client = client.with_options(timeout=1.0)
        assert new_client is not client


# ---------------------------------------------------------------------------
# 4. Custom HTTP client
# ---------------------------------------------------------------------------


class TestCustomHttpClient:
    def test_custom_http_client_aliases_exported(self):
        assert DefaultHttpxClient is httpx.Client
        assert DefaultAsyncHttpxClient is httpx.AsyncClient

    def test_sync_client_uses_custom_http_client(self):
        custom = httpx.Client()
        client = SyncClient(api_key="lb_test", http_client=custom)
        assert client._get_http_client() is custom
        custom.close()

    def test_async_client_uses_custom_http_client(self):
        custom = httpx.AsyncClient()
        client = AsyncClient(api_key="lb_test", http_client=custom)
        assert client._get_http_client() is custom

        async def cleanup():
            await custom.aclose()

        asyncio.get_event_loop().run_until_complete(cleanup())


# ---------------------------------------------------------------------------
# 5. Idempotency key auto-generation
# ---------------------------------------------------------------------------


class TestIdempotencyKey:
    def _mock_response(self, status: int = 200, json_body: dict | None = None) -> httpx.Response:
        return httpx.Response(
            status_code=status,
            json=json_body or {"object": "ok"},
            request=httpx.Request("POST", "https://api.listbee.so/v1/test"),
        )

    def test_idempotency_key_added_to_post(self):
        client = SyncClient(api_key="lb_test", max_retries=3)
        captured_headers: dict = {}

        def mock_request(method, path, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            return self._mock_response()

        with patch.object(client._get_http_client(), "request", side_effect=mock_request):
            client._request("POST", "/v1/test", json={})

        assert "Idempotency-Key" in captured_headers
        key = captured_headers["Idempotency-Key"]
        # UUID format: 8-4-4-4-12
        assert len(key) == 36
        assert key.count("-") == 4

    def test_idempotency_key_added_to_put(self):
        client = SyncClient(api_key="lb_test", max_retries=1)
        captured_headers: dict = {}

        def mock_request(method, path, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            return self._mock_response()

        with patch.object(client._get_http_client(), "request", side_effect=mock_request):
            client._request("PUT", "/v1/test", json={})

        assert "Idempotency-Key" in captured_headers

    def test_no_idempotency_key_on_get(self):
        client = SyncClient(api_key="lb_test", max_retries=3)
        captured_headers: dict = {}

        def mock_request(method, path, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            return self._mock_response()

        with patch.object(client._get_http_client(), "request", side_effect=mock_request):
            client._request("GET", "/v1/test")

        assert "Idempotency-Key" not in captured_headers

    def test_no_idempotency_key_when_max_retries_zero(self):
        client = SyncClient(api_key="lb_test", max_retries=0)
        captured_headers: dict = {}

        def mock_request(method, path, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            return self._mock_response()

        with patch.object(client._get_http_client(), "request", side_effect=mock_request):
            client._request("POST", "/v1/test", json={})

        assert "Idempotency-Key" not in captured_headers

    def test_idempotency_key_stable_across_retries(self):
        """Same key used on all retry attempts."""
        client = SyncClient(api_key="lb_test", max_retries=2)
        captured_keys: list[str] = []
        call_count = 0

        def mock_request(method, path, **kwargs):
            nonlocal call_count
            call_count += 1
            key = kwargs.get("headers", {}).get("Idempotency-Key")
            if key:
                captured_keys.append(key)
            # First call returns 429 to trigger retry; second returns 200
            if call_count == 1:
                return httpx.Response(
                    status_code=429,
                    json=_error_body(status=429, code="rate_limited"),
                    headers={"retry-after": "0"},
                    request=httpx.Request("POST", "https://api.listbee.so/v1/test"),
                )
            return self._mock_response()

        with patch.object(client._get_http_client(), "request", side_effect=mock_request):
            client._request("POST", "/v1/test", json={})

        assert len(captured_keys) == 2
        assert captured_keys[0] == captured_keys[1]


# ---------------------------------------------------------------------------
# 6. with_raw_response
# ---------------------------------------------------------------------------


class TestWithRawResponse:
    def test_raw_response_has_status_code(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"x-request-id": "req_xyz", "content-type": "application/json"}
        mock_response.json.return_value = _make_account_dict()

        raw = RawResponse(mock_response, AccountResponse)
        assert raw.status_code == 200

    def test_raw_response_has_request_id(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"x-request-id": "req_xyz"}
        mock_response.json.return_value = _make_account_dict()

        raw = RawResponse(mock_response, AccountResponse)
        assert raw.request_id == "req_xyz"

    def test_raw_response_request_id_none_when_absent(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = _make_account_dict()

        raw = RawResponse(mock_response, AccountResponse)
        assert raw.request_id is None

    def test_raw_response_parse_returns_model(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"x-request-id": "req_parse"}
        mock_response.json.return_value = _make_account_dict()

        raw = RawResponse(mock_response, AccountResponse)
        account = raw.parse()
        assert isinstance(account, AccountResponse)
        assert account.id == "acc_test"

    def test_raw_response_headers_dict(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"x-request-id": "req_hdr", "content-type": "application/json"}
        mock_response.json.return_value = _make_account_dict()

        raw = RawResponse(mock_response, AccountResponse)
        assert raw.headers["x-request-id"] == "req_hdr"
        assert raw.headers["content-type"] == "application/json"

    def test_account_with_raw_response_proxy(self):
        """with_raw_response property on Account resource calls request_raw."""
        client = ListBee(api_key="lb_test")

        mock_raw = MagicMock()
        mock_raw.status_code = 200
        mock_raw.headers = {"x-request-id": "req_account"}
        mock_raw.json.return_value = _make_account_dict()

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.account.with_raw_response.get()

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_account"
        account = raw.parse()
        assert account.id == "acc_test"

    def test_listings_with_raw_response_proxy(self):
        """with_raw_response on Listings calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 200
        mock_raw.headers = {"x-request-id": "req_listing"}
        mock_raw.json.return_value = {
            "object": "listing",
            "id": "lst_test",
            "name": "Test Listing",
            "price": 1000,
            "status": "draft",
            "slug": "test-listing",
            "currency": "USD",
            "content_type": "static",
            "checkout_url": "https://checkout.listbee.so/test-listing",
            "cover_url": None,
            "description": None,
            "tagline": None,
            "highlights": [],
            "cta": None,
            "metadata": None,
            "compare_at_price": None,
            "badges": [],
            "cover_blur": "auto",
            "rating": None,
            "rating_count": None,
            "reviews": [],
            "faqs": [],
            "utm_source": None,
            "utm_medium": None,
            "utm_campaign": None,
            "deliverables": [],
            "has_cover": False,
            "readiness": {"sellable": False, "actions": [], "next": None},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.listings.with_raw_response.get("lst_test")

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_listing"
        listing = raw.parse()
        assert listing.id == "lst_test"

    def test_orders_with_raw_response_proxy(self):
        """with_raw_response on Orders calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 200
        mock_raw.headers = {"x-request-id": "req_order"}
        mock_raw.json.return_value = {
            "object": "order",
            "id": "ord_test",
            "status": "paid",
            "payment_status": "paid",
            "listing_id": "lst_abc",
            "buyer_email": "buyer@example.com",
            "amount": 1000,
            "currency": "USD",
            "content_type": "static",
            "stripe_payment_intent_id": "pi_test",
            "listing_snapshot": None,
            "seller_snapshot": None,
            "handed_off_at": None,
            "checkout_data": {},
            "deliverables": [],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.orders.with_raw_response.get("ord_test")

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_order"
        order = raw.parse()
        assert order.id == "ord_test"

    def test_webhooks_with_raw_response_proxy(self):
        """with_raw_response on Webhooks calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 200
        mock_raw.headers = {"x-request-id": "req_webhook"}
        mock_raw.json.return_value = {
            "object": "webhook_test",
            "status": "delivered",
            "delivered_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.webhooks.with_raw_response.test("wh_abc")

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_webhook"

    def test_api_keys_with_raw_response_proxy(self):
        """with_raw_response on ApiKeys calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 201
        mock_raw.headers = {"x-request-id": "req_apikey"}
        mock_raw.json.return_value = {
            "object": "api_key",
            "id": "lbk_test",
            "name": "My Key",
            "key": "lb_secretvalue",
            "prefix": "lb_secr",
            "created_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.api_keys.with_raw_response.create(name="My Key")

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_apikey"
        key = raw.parse()
        assert key.id == "lbk_test"

    def test_customers_with_raw_response_proxy(self):
        """with_raw_response on Customers calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 200
        mock_raw.headers = {"x-request-id": "req_customer"}
        mock_raw.json.return_value = {
            "object": "customer",
            "id": "cus_test",
            "email": "buyer@example.com",
            "order_count": 3,
            "total_orders": 3,
            "total_spent": 9900,
            "currency": "USD",
            "created_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.customers.with_raw_response.get("cus_test")

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_customer"
        customer = raw.parse()
        assert customer.id == "cus_test"

    def test_stripe_with_raw_response_proxy(self):
        """with_raw_response on Stripe calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 201
        mock_raw.headers = {"x-request-id": "req_stripe"}
        mock_raw.json.return_value = {
            "object": "stripe_connect_session",
            "url": "https://connect.stripe.com/setup/s/test",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.stripe.with_raw_response.connect()

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_stripe"

    def test_utility_with_raw_response_proxy(self):
        """with_raw_response on Utility calls request_raw and returns RawResponse."""
        client = ListBee(api_key="lb_test")
        mock_raw = MagicMock()
        mock_raw.status_code = 200
        mock_raw.headers = {"x-request-id": "req_ping"}
        mock_raw.json.return_value = {
            "object": "ping",
            "status": "ok",
            "version": "1.0.0",
        }

        with patch.object(client, "request_raw", return_value=mock_raw):
            raw = client.utility.with_raw_response.ping()

        assert isinstance(raw, RawResponse)
        assert raw.request_id == "req_ping"
        ping = raw.parse()
        assert ping.status == "ok"
