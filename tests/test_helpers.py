"""Tests for helper utilities: price formatting, readiness helpers, order/listing
state properties, webhook parsing, and action resolution."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from unittest.mock import MagicMock

import pytest

from listbee._exceptions import WebhookVerificationError
from listbee.helpers import (
    ParsedWebhookEvent,
    format_price,
    from_minor,
    parse_webhook_event,
    resolve_action,
    to_minor,
)
from listbee.types.listing import ListingDetailResponse
from listbee.types.order import OrderResponse
from listbee.types.shared import (
    AccountReadiness,
    Action,
    ActionCode,
    ActionKind,
    ActionResolve,
    ListingReadiness,
    WebhookEventType,
)

SECRET = "whsec_testsecret123"


def _build_sig(body: str, secret: str = SECRET, timestamp: int | None = None) -> str:
    ts = str(timestamp or int(time.time()))
    signed_content = f"{ts}.{body}"
    sig = hmac.new(secret.encode(), signed_content.encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


# ---------------------------------------------------------------------------
# Price helpers
# ---------------------------------------------------------------------------


class TestFormatPrice:
    def test_usd(self):
        assert format_price(2900, "USD") == "$29.00"

    def test_usd_uppercase_currency(self):
        assert format_price(2900, "USD") == "$29.00"

    def test_eur(self):
        assert format_price(1999, "EUR") == "\u20ac19.99"

    def test_gbp(self):
        assert format_price(500, "GBP") == "\u00a35.00"

    def test_jpy_zero_decimal(self):
        assert format_price(1500, "JPY") == "\u00a51,500"

    def test_jpy_lowercase(self):
        assert format_price(1500, "jpy") == "\u00a51,500"

    def test_krw_zero_decimal(self):
        assert format_price(10000, "KRW") == "\u20a910,000"

    def test_unknown_currency_fallback(self):
        result = format_price(1000, "XYZ")
        assert "XYZ" in result
        assert "10.00" in result

    def test_zero_amount_usd(self):
        assert format_price(0, "USD") == "$0.00"

    def test_large_amount_with_comma(self):
        result = format_price(100000, "USD")
        assert "1,000.00" in result


class TestToMinor:
    def test_usd(self):
        assert to_minor(29.00, "USD") == 2900

    def test_usd_fractional(self):
        assert to_minor(19.99, "USD") == 1999

    def test_jpy_zero_decimal(self):
        assert to_minor(1500, "JPY") == 1500

    def test_eur(self):
        assert to_minor(9.99, "EUR") == 999

    def test_zero(self):
        assert to_minor(0, "USD") == 0


class TestFromMinor:
    def test_usd(self):
        assert from_minor(2900, "USD") == 29.0

    def test_usd_fractional(self):
        assert from_minor(1999, "USD") == 19.99

    def test_jpy_zero_decimal(self):
        assert from_minor(1500, "JPY") == 1500.0

    def test_eur(self):
        assert from_minor(999, "EUR") == 9.99

    def test_zero(self):
        assert from_minor(0, "USD") == 0.0


# ---------------------------------------------------------------------------
# Readiness helpers
# ---------------------------------------------------------------------------

API_ACTION = Action(
    code=ActionCode.LISTING_DELIVERABLE_MISSING,
    kind=ActionKind.API,
    message="Attach a deliverable to this listing",
    resolve=ActionResolve(method="PUT", endpoint="/v1/listings/lst_abc123", url=None, params=None),
)

HUMAN_ACTION = Action(
    code=ActionCode.STRIPE_CONNECT_REQUIRED,
    kind=ActionKind.HUMAN,
    message="Connect Stripe in the dashboard",
    resolve=ActionResolve(method="GET", endpoint=None, url="https://listbee.so/connect/stripe", params=None),
)


class TestListingReadiness:
    def test_is_ready_when_buyable(self):
        r = ListingReadiness(buyable=True, actions=[], next=None)
        assert r.is_ready is True

    def test_is_ready_when_not_buyable(self):
        r = ListingReadiness(buyable=False, actions=[API_ACTION], next="listing_deliverable_missing")
        assert r.is_ready is False

    def test_next_action_returns_matching_action(self):
        r = ListingReadiness(buyable=False, actions=[API_ACTION], next="listing_deliverable_missing")
        assert r.next_action is API_ACTION

    def test_next_action_returns_none_when_ready(self):
        r = ListingReadiness(buyable=True, actions=[], next=None)
        assert r.next_action is None

    def test_next_action_returns_none_when_no_match(self):
        r = ListingReadiness(buyable=False, actions=[API_ACTION], next="nonexistent_code")
        assert r.next_action is None

    def test_actions_by_kind_api(self):
        r = ListingReadiness(buyable=False, actions=[API_ACTION, HUMAN_ACTION], next="listing_deliverable_missing")
        result = r.actions_by_kind("api")
        assert result == [API_ACTION]

    def test_actions_by_kind_human(self):
        r = ListingReadiness(buyable=False, actions=[API_ACTION, HUMAN_ACTION], next="listing_deliverable_missing")
        result = r.actions_by_kind("human")
        assert result == [HUMAN_ACTION]

    def test_actions_by_kind_empty(self):
        r = ListingReadiness(buyable=True, actions=[], next=None)
        assert r.actions_by_kind("api") == []


class TestAccountReadiness:
    def test_is_ready_when_operational(self):
        r = AccountReadiness(operational=True, actions=[], next=None)
        assert r.is_ready is True

    def test_is_ready_when_not_operational(self):
        r = AccountReadiness(operational=False, actions=[HUMAN_ACTION], next="stripe_connect_required")
        assert r.is_ready is False

    def test_next_action_returns_matching_action(self):
        r = AccountReadiness(operational=False, actions=[HUMAN_ACTION], next="stripe_connect_required")
        assert r.next_action is HUMAN_ACTION

    def test_next_action_returns_none_when_ready(self):
        r = AccountReadiness(operational=True, actions=[], next=None)
        assert r.next_action is None

    def test_actions_by_kind(self):
        r = AccountReadiness(operational=False, actions=[API_ACTION, HUMAN_ACTION], next="stripe_connect_required")
        assert r.actions_by_kind("human") == [HUMAN_ACTION]
        assert r.actions_by_kind("api") == [API_ACTION]


# ---------------------------------------------------------------------------
# Order state helpers
# ---------------------------------------------------------------------------

BASE_ORDER = {
    "object": "order",
    "id": "ord_9xM4kP7nR2qT5wY1",
    "listing_id": "lst_abc123",
    "buyer_email": "buyer@example.com",
    "amount": 2999,
    "currency": "USD",
    "stripe_payment_intent_id": "pi_3abc123def456",
    "status": "paid",
    "payment_status": "paid",
    "actions": None,
    "checkout_data": None,
    "listing_snapshot": None,
    "seller_snapshot": None,
    "deliverable": None,
    "metadata": None,
    "unlock_url": None,
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


class TestOrderStateHelpers:
    def _make(self, **overrides: object) -> OrderResponse:
        return OrderResponse(**{**BASE_ORDER, **overrides})

    def test_is_paid_true(self):
        order = self._make(payment_status="paid")
        assert order.is_paid is True

    def test_is_paid_false(self):
        order = self._make(payment_status="unpaid")
        assert order.is_paid is False

    def test_is_refunded_true(self):
        order = self._make(payment_status="refunded")
        assert order.is_refunded is True

    def test_is_refunded_false(self):
        order = self._make(payment_status="paid")
        assert order.is_refunded is False

    def test_is_disputed_true(self):
        order = self._make(dispute_status="needs_response")
        assert order.is_disputed is True

    def test_is_disputed_false(self):
        order = self._make(dispute_status=None)
        assert order.is_disputed is False

    def test_needs_fulfillment_true(self):
        order = self._make(status="paid")
        assert order.needs_fulfillment is True

    def test_needs_fulfillment_false_wrong_status(self):
        order = self._make(status="fulfilled")
        assert order.needs_fulfillment is False

    def test_is_terminal_fulfilled(self):
        order = self._make(status="fulfilled")
        assert order.is_terminal is True

    def test_is_terminal_false_for_paid(self):
        order = self._make(status="paid")
        assert order.is_terminal is False


# ---------------------------------------------------------------------------
# Listing lifecycle helpers
# ---------------------------------------------------------------------------

BASE_LISTING = {
    "object": "listing",
    "id": "lst_abc123",
    "url": "https://buy.listbee.so/lst_abc123/seo-playbook",
    "name": "SEO Playbook",
    "description": None,
    "tagline": None,
    "highlights": [],
    "cta": None,
    "price": 2900,
    "currency": "usd",
    "fulfillment_mode": "MANAGED",
    "image_url": None,
    "deliverable": None,
    "agent_callback_url": None,
    "checkout_schema": None,
    "compare_at_price": None,
    "badges": [],
    "rating": None,
    "rating_count": None,
    "reviews": [],
    "faqs": [],
    "metadata": None,
    "status": "published",
    "readiness": {"buyable": True, "actions": [], "next": None},
    "created_at": "2026-03-30T12:00:00Z",
    "stats": {"schema_version": 1, "views": 0, "purchases": 0, "gmv_minor": 0},
}


class TestListingLifecycleHelpers:
    def _make(self, **overrides: object) -> ListingDetailResponse:
        return ListingDetailResponse(**{**BASE_LISTING, **overrides})

    def test_is_draft_true(self):
        listing = self._make(status="draft")
        assert listing.is_draft is True

    def test_is_draft_false(self):
        listing = self._make(status="published")
        assert listing.is_draft is False

    def test_is_published_true(self):
        listing = self._make(status="published")
        assert listing.is_published is True

    def test_is_published_false(self):
        listing = self._make(status="draft")
        assert listing.is_published is False

    def test_checkout_url_returns_url(self):
        listing = self._make(url="https://buy.listbee.so/lst_abc123/seo-playbook")
        assert listing.checkout_url == "https://buy.listbee.so/lst_abc123/seo-playbook"


# ---------------------------------------------------------------------------
# parse_webhook_event
# ---------------------------------------------------------------------------


class TestParseWebhookEvent:
    def _make_payload_and_header(self, event_type: str, data: dict) -> tuple[str, str]:
        body = json.dumps({"event_type": event_type, "data": data})
        header = _build_sig(body)
        return body, header

    def test_order_paid_event(self):
        data = {"id": "ord_abc", "amount": 2900}
        body, header = self._make_payload_and_header("order.paid", data)
        event = parse_webhook_event(body, header, SECRET)
        assert event.type == WebhookEventType.ORDER_PAID
        assert event.data == data

    def test_order_fulfilled_event(self):
        data = {"id": "ord_xyz"}
        body, header = self._make_payload_and_header("order.fulfilled", data)
        event = parse_webhook_event(body, header, SECRET)
        assert event.type == WebhookEventType.ORDER_FULFILLED

    def test_listing_published_event(self):
        data = {"slug": "seo-playbook"}
        body, header = self._make_payload_and_header("listing.published", data)
        event = parse_webhook_event(body, header, SECRET)
        assert event.type == WebhookEventType.LISTING_PUBLISHED

    def test_bytes_payload(self):
        data = {"id": "ord_bytes"}
        body_str = json.dumps({"event_type": "order.paid", "data": data})
        body_bytes = body_str.encode()
        header = _build_sig(body_str)
        event = parse_webhook_event(body_bytes, header, SECRET)
        assert event.type == WebhookEventType.ORDER_PAID

    def test_returns_parsed_webhook_event_instance(self):
        data = {}
        body, header = self._make_payload_and_header("order.paid", data)
        event = parse_webhook_event(body, header, SECRET)
        assert isinstance(event, ParsedWebhookEvent)

    def test_invalid_signature_raises(self):
        data = {}
        body, _ = self._make_payload_and_header("order.paid", data)
        bad_header = _build_sig(body, secret="whsec_wrong")
        with pytest.raises(WebhookVerificationError):
            parse_webhook_event(body, bad_header, SECRET)

    def test_expired_timestamp_raises(self):
        data = {}
        body_str = json.dumps({"event_type": "order.paid", "data": data})
        old_ts = int(time.time()) - 600
        header = _build_sig(body_str, timestamp=old_ts)
        with pytest.raises(WebhookVerificationError, match="tolerance"):
            parse_webhook_event(body_str, header, SECRET, tolerance=300)


# ---------------------------------------------------------------------------
# resolve_action — ValueError for human actions
# ---------------------------------------------------------------------------


class TestResolveAction:
    def test_raises_for_human_action_with_no_endpoint(self):
        action = Action(
            code=ActionCode.STRIPE_CONNECT_REQUIRED,
            kind=ActionKind.HUMAN,
            message="Connect Stripe",
            resolve=ActionResolve(
                method="GET",
                endpoint=None,
                url="https://listbee.so/connect/stripe",
                params=None,
            ),
        )
        mock_client = MagicMock()
        with pytest.raises(ValueError, match="human intervention"):
            resolve_action(mock_client, action)

    def test_post_action_calls_client_post(self):
        action = Action(
            code=ActionCode.LISTING_DELIVERABLE_MISSING,
            kind=ActionKind.API,
            message="Attach a deliverable",
            resolve=ActionResolve(
                method="POST",
                endpoint="/v1/listings/slug/deliverables",
                url=None,
                params={"type": "url", "value": "https://example.com"},
            ),
        )
        mock_client = MagicMock()
        mock_client.post.return_value.json.return_value = {"object": "deliverable"}
        result = resolve_action(mock_client, action)
        mock_client.post.assert_called_once_with(
            "/v1/listings/slug/deliverables",
            json={"type": "url", "value": "https://example.com"},
        )
        assert result == {"object": "deliverable"}

    def test_get_action_calls_client_get(self):
        action = Action(
            code=ActionCode.LISTING_DELIVERABLE_MISSING,
            kind=ActionKind.API,
            message="Get something",
            resolve=ActionResolve(
                method="GET",
                endpoint="/v1/account",
                url=None,
                params=None,
            ),
        )
        mock_client = MagicMock()
        mock_client.get.return_value.json.return_value = {"object": "account"}
        result = resolve_action(mock_client, action)
        mock_client.get.assert_called_once_with("/v1/account")
        assert result == {"object": "account"}

    def test_delete_action_returns_none(self):
        action = Action(
            code=ActionCode.LISTING_DELIVERABLE_MISSING,
            kind=ActionKind.API,
            message="Delete something",
            resolve=ActionResolve(
                method="DELETE",
                endpoint="/v1/listings/slug/deliverables/del_001",
                url=None,
                params=None,
            ),
        )
        mock_client = MagicMock()
        result = resolve_action(mock_client, action)
        mock_client.delete.assert_called_once_with("/v1/listings/slug/deliverables/del_001")
        assert result is None

    def test_put_action_calls_client_put(self):
        action = Action(
            code=ActionCode.FULFILLMENT_PENDING,
            kind=ActionKind.API,
            message="Configure webhook",
            resolve=ActionResolve(
                method="PUT",
                endpoint="/v1/webhooks/wh_abc",
                url=None,
                params={"enabled": True},
            ),
        )
        mock_client = MagicMock()
        mock_client.put.return_value.json.return_value = {"object": "webhook"}
        result = resolve_action(mock_client, action)
        mock_client.put.assert_called_once_with(
            "/v1/webhooks/wh_abc",
            json={"enabled": True},
        )
        assert result == {"object": "webhook"}

    def test_post_action_with_no_params_sends_empty_dict(self):
        action = Action(
            code=ActionCode.LISTING_UNPUBLISHED,
            kind=ActionKind.API,
            message="Publish listing",
            resolve=ActionResolve(
                method="POST",
                endpoint="/v1/listings/slug/publish",
                url=None,
                params=None,
            ),
        )
        mock_client = MagicMock()
        mock_client.post.return_value.json.return_value = {"object": "listing"}
        resolve_action(mock_client, action)
        mock_client.post.assert_called_once_with("/v1/listings/slug/publish", json={})
