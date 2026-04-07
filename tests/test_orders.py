"""Tests for the Orders resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.deliverable import Deliverable
from listbee.resources.orders import Orders
from listbee.types.order import OrderResponse

ORDER_JSON = {
    "object": "order",
    "id": "ord_9xM4kP7nR2qT5wY1",
    "listing_id": "lst_abc123",
    "buyer_email": "buyer@example.com",
    "amount": 2999,
    "currency": "USD",
    "stripe_payment_intent_id": "pi_3abc123def456",
    "status": "paid",
    "checkout_data": None,
    "shipping_address": None,
    "deliverables": [],
    "paid_at": "2026-03-28T12:00:01Z",
    "fulfilled_at": None,
    "refund_amount": 0,
    "refunded_at": None,
    "dispute_amount": 0,
    "dispute_reason": None,
    "dispute_status": None,
    "disputed_at": None,
    "platform_fee": 0,
    "created_at": "2026-03-28T12:00:00Z",
}

ORDER_WITH_CHECKOUT_DATA_JSON = {
    **ORDER_JSON,
    "id": "ord_checkout123",
    "checkout_data": {"shirt_size": "L", "color": "Blue"},
    "shipping_address": {
        "line1": "123 Main St",
        "line2": "Apt 4B",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94105",
        "country": "US",
    },
}

FULFILLED_ORDER_JSON = {
    **ORDER_JSON,
    "id": "ord_fulfilled123",
    "status": "fulfilled",
    "deliverables": [
        {
            "object": "deliverable",
            "id": "del_existing_001",
            "type": "file",
            "status": "ready",
            "content": None,
            "filename": "ebook.pdf",
            "mime_type": "application/pdf",
            "size": 2458631,
            "url": None,
        }
    ],
    "fulfilled_at": "2026-03-28T13:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def orders(sync_client):
    return Orders(sync_client)


class TestGetOrder:
    def test_get_order_returns_order_response(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_9xM4kP7nR2qT5wY1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_9xM4kP7nR2qT5wY1")
        assert isinstance(result, OrderResponse)
        assert result.id == "ord_9xM4kP7nR2qT5wY1"
        assert result.buyer_email == "buyer@example.com"
        assert result.amount == 2999
        assert result.currency == "USD"
        assert result.status == "paid"

    def test_get_order_sends_correct_path(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders/ord_abc").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            orders.get("ord_abc")
        assert route.called

    def test_get_order_no_stripe_session_id(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_9xM4kP7nR2qT5wY1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_9xM4kP7nR2qT5wY1")
        assert not hasattr(result, "stripe_session_id")


class TestListOrders:
    def test_list_orders_returns_items(self, orders):
        page_json = {
            "data": [ORDER_JSON],
            "has_more": False,
            "total_count": 1,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            results = list(orders.list())
        assert len(results) == 1
        assert isinstance(results[0], OrderResponse)
        assert results[0].id == "ord_9xM4kP7nR2qT5wY1"

    def test_list_orders_with_status_filter(self, orders):
        page_json = {"data": [ORDER_JSON], "has_more": False, "total_count": 1, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(status="paid"))
        assert "status=paid" in str(route.calls[0].request.url)

    def test_list_orders_without_status_filter_omits_param(self, orders):
        page_json = {"data": [], "has_more": False, "total_count": 0, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list())
        assert "status" not in str(route.calls[0].request.url)

    def test_list_orders_with_listing_filter(self, orders):
        page_json = {"data": [ORDER_JSON], "has_more": False, "total_count": 1, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(listing="seo-playbook"))
        assert "listing=seo-playbook" in str(route.calls[0].request.url)

    def test_list_orders_with_created_after_string(self, orders):
        page_json = {"data": [], "has_more": False, "total_count": 0, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(created_after="2026-01-01T00:00:00Z"))
        assert "created_after=2026-01-01T00" in str(route.calls[0].request.url)

    def test_list_orders_with_created_before_datetime(self, orders):
        from datetime import datetime, timezone

        page_json = {"data": [], "has_more": False, "total_count": 0, "cursor": None}
        dt = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(created_before=dt))
        assert "created_before=2026-03-30T12" in str(route.calls[0].request.url)

    def test_list_orders_total_count(self, orders):
        page_json = {"data": [ORDER_JSON], "has_more": False, "total_count": 99, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            page = orders.list()
        assert page.total_count == 99


class TestOrderStatus:
    def test_order_pending_status(self, orders):
        pending_json = {**ORDER_JSON, "status": "pending", "paid_at": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=pending_json))
            result = orders.get("ord_1")
        assert result.status == "pending"
        assert result.paid_at is None

    def test_order_paid_status(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_1")
        assert result.status == "paid"
        assert result.paid_at is not None

    def test_order_fulfilled_status(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON))
            result = orders.get("ord_1")
        assert result.status == "fulfilled"
        assert len(result.deliverables) == 1
        assert result.deliverables[0].type == "file"
        assert result.deliverables[0].status == "ready"
        assert result.fulfilled_at is not None

    def test_order_canceled_status(self, orders):
        canceled_json = {**ORDER_JSON, "status": "canceled"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=canceled_json))
            result = orders.get("ord_1")
        assert result.status == "canceled"

    def test_order_failed_status(self, orders):
        failed_json = {**ORDER_JSON, "status": "failed"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=failed_json))
            result = orders.get("ord_1")
        assert result.status == "failed"


class TestOrderCheckoutData:
    def test_order_with_checkout_data(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_checkout123").mock(
                return_value=httpx.Response(200, json=ORDER_WITH_CHECKOUT_DATA_JSON)
            )
            result = orders.get("ord_checkout123")
        assert result.checkout_data == {"shirt_size": "L", "color": "Blue"}

    def test_order_with_shipping_address(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_checkout123").mock(
                return_value=httpx.Response(200, json=ORDER_WITH_CHECKOUT_DATA_JSON)
            )
            result = orders.get("ord_checkout123")
        assert result.shipping_address is not None
        assert result.shipping_address.line1 == "123 Main St"
        assert result.shipping_address.line2 == "Apt 4B"
        assert result.shipping_address.city == "San Francisco"
        assert result.shipping_address.state == "CA"
        assert result.shipping_address.postal_code == "94105"
        assert result.shipping_address.country == "US"

    def test_order_without_checkout_data(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_9xM4kP7nR2qT5wY1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_9xM4kP7nR2qT5wY1")
        assert result.checkout_data is None
        assert result.shipping_address is None


class TestFulfillOrder:
    def test_fulfill_order_without_deliverables(self, orders):
        """Close out an order without pushing content."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            result = orders.fulfill("ord_9xM4kP7nR2qT5wY1")
        assert isinstance(result, OrderResponse)
        assert result.status == "fulfilled"
        body = json.loads(route.calls[0].request.content)
        assert "deliverables" not in body

    def test_fulfill_order_with_text(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            result = orders.fulfill(
                "ord_9xM4kP7nR2qT5wY1",
                deliverables=[{"type": "text", "value": "Here is your AI-generated report"}],
            )
        assert isinstance(result, OrderResponse)
        assert result.status == "fulfilled"
        body = json.loads(route.calls[0].request.content)
        assert body["deliverables"] == [{"type": "text", "value": "Here is your AI-generated report"}]

    def test_fulfill_order_with_url(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            orders.fulfill(
                "ord_9xM4kP7nR2qT5wY1",
                deliverables=[{"type": "url", "value": "https://example.com/generated.pdf"}],
            )
        body = json.loads(route.calls[0].request.content)
        assert body["deliverables"][0]["value"] == "https://example.com/generated.pdf"

    def test_fulfill_order_sends_deliverables_key(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            orders.fulfill("ord_9xM4kP7nR2qT5wY1", deliverables=[{"type": "text", "value": "some content"}])
        body = json.loads(route.calls[0].request.content)
        assert "deliverables" in body

    def test_fulfill_order_sends_correct_path(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_abc/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            orders.fulfill("ord_abc", deliverables=[{"type": "text", "value": "some content"}])
        assert route.called


class TestRefundOrder:
    def test_refund_returns_order_response(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/orders/ord_abc123/refund").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.refund("ord_abc123")
        assert isinstance(result, OrderResponse)

    def test_refund_sends_correct_path(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_abc/refund").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            orders.refund("ord_abc")
        assert route.called


class TestFulfillWithDeliverableClass:
    @respx.mock
    def test_fulfill_with_file(self, sync_client):
        respx.post("https://api.listbee.so/v1/files").mock(
            return_value=httpx.Response(
                201,
                json={
                    "object": "file",
                    "id": "file_tok_abc",
                    "filename": "report.pdf",
                    "size": 1024,
                    "mime_type": "application/pdf",
                    "purpose": "deliverable",
                    "expires_at": "2026-04-07T12:00:00Z",
                    "created_at": "2026-04-06T12:00:00Z",
                },
            )
        )
        route = respx.post("https://api.listbee.so/v1/orders/ord_abc/fulfill").mock(
            return_value=httpx.Response(200, json=ORDER_JSON)
        )
        result = Orders(sync_client).fulfill(
            "ord_abc",
            deliverables=[Deliverable.file(b"content", filename="report.pdf")],
        )
        assert result.id == ORDER_JSON["id"]
        sent = json.loads(route.calls[0].request.content)
        assert sent["deliverables"][0] == {"type": "file", "token": "file_tok_abc"}

    @respx.mock
    def test_fulfill_with_text(self, sync_client):
        route = respx.post("https://api.listbee.so/v1/orders/ord_abc/fulfill").mock(
            return_value=httpx.Response(200, json=ORDER_JSON)
        )
        Orders(sync_client).fulfill(
            "ord_abc",
            deliverables=[Deliverable.text("Your report")],
        )
        sent = json.loads(route.calls[0].request.content)
        assert sent == {"deliverables": [{"type": "text", "value": "Your report"}]}

    @respx.mock
    def test_fulfill_without_deliverables_sends_empty_body(self, sync_client):
        route = respx.post("https://api.listbee.so/v1/orders/ord_abc/fulfill").mock(
            return_value=httpx.Response(200, json=ORDER_JSON)
        )
        Orders(sync_client).fulfill("ord_abc")
        sent = json.loads(route.calls[0].request.content)
        assert sent == {}
