"""Tests for the Orders resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.deliverable import Deliverable
from listbee.resources.orders import Orders
from listbee.types.order import OrderResponse, OrderSummary
from listbee.types.order_redeliver import RedeliveryAck

ORDER_JSON = {
    "object": "order",
    "id": "ord_9xM4kP7nR2qT5wY1",
    "listing_id": "lst_abc123",
    "buyer_email": "buyer@example.com",
    "amount": 2999,
    "currency": "USD",
    "stripe_payment_intent_id": "pi_3abc123def456",
    "status": "paid",
    "payment_status": "paid",
    "has_deliverables": False,
    "deliverable": None,
    "metadata": None,
    "unlock_url": None,
    "actions": None,
    "readiness": None,
    "checkout_data": None,
    "listing_snapshot": {"name": "SEO Playbook", "price": 2999, "slug": "seo-playbook"},
    "seller_snapshot": {"display_name": "Acme Agency"},
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
}

FULFILLED_ORDER_JSON = {
    **ORDER_JSON,
    "id": "ord_fulfilled123",
    "status": "fulfilled",
    "has_deliverables": True,
    "deliverable": {
        "object": "deliverable",
        "id": "del_existing_001",
        "type": "text",
        "status": "ready",
        "url": None,
        "content": "Your personalized report content...",
    },
    "unlock_url": "https://buy.listbee.so/dl/ord_fulfilled123?token=abc",
    "fulfilled_at": "2026-03-28T13:00:00Z",
}

ORDER_SUMMARY_JSON = {
    "object": "order",
    "id": "ord_9xM4kP7nR2qT5wY1",
    "listing_id": "lst_abc123",
    "buyer_email": "buyer@example.com",
    "amount": 2999,
    "currency": "USD",
    "status": "paid",
    "payment_status": "paid",
    "platform_fee": 0,
    "refund_amount": 0,
    "dispute_status": None,
    "paid_at": "2026-03-28T12:00:01Z",
    "fulfilled_at": None,
    "created_at": "2026-03-28T12:00:00Z",
}

REDELIVER_ACK_JSON = {
    "object": "redelivery_ack",
    "order_id": "ord_9xM4kP7nR2qT5wY1",
    "scheduled_attempts": 2,
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

    def test_get_order_has_new_fields(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_9xM4kP7nR2qT5wY1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_9xM4kP7nR2qT5wY1")
        assert result.deliverable is None
        assert result.metadata is None
        assert result.unlock_url is None

    def test_get_order_fulfilled_has_deliverable_and_unlock_url(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_fulfilled123").mock(return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON))
            result = orders.get("ord_fulfilled123")
        assert result.deliverable is not None
        assert result.deliverable.type == "text"
        assert result.deliverable.content == "Your personalized report content..."
        assert result.unlock_url == "https://buy.listbee.so/dl/ord_fulfilled123?token=abc"


class TestListOrders:
    def test_list_orders_returns_summary_items(self, orders):
        page_json = {
            "data": [ORDER_SUMMARY_JSON],
            "has_more": False,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            results = list(orders.list())
        assert len(results) == 1
        assert isinstance(results[0], OrderSummary)
        assert results[0].id == "ord_9xM4kP7nR2qT5wY1"

    def test_list_orders_with_status_filter(self, orders):
        page_json = {"data": [ORDER_SUMMARY_JSON], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(status="paid"))
        assert "status=paid" in str(route.calls[0].request.url)

    def test_list_orders_without_status_filter_omits_param(self, orders):
        page_json = {"data": [], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list())
        assert "status" not in str(route.calls[0].request.url)

    def test_list_orders_with_listing_filter(self, orders):
        page_json = {"data": [ORDER_SUMMARY_JSON], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(listing="lst_abc123"))
        assert "listing=" in str(route.calls[0].request.url)

    def test_list_orders_with_created_after_string(self, orders):
        page_json = {"data": [], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(created_after="2026-01-01T00:00:00Z"))
        assert "created_after=2026-01-01T00" in str(route.calls[0].request.url)

    def test_list_orders_with_created_before_datetime(self, orders):
        from datetime import datetime, timezone

        page_json = {"data": [], "has_more": False, "cursor": None}
        dt = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(created_before=dt))
        assert "created_before=2026-03-30T12" in str(route.calls[0].request.url)

    def test_list_orders_has_more_and_cursor(self, orders):
        page_json = {"data": [ORDER_SUMMARY_JSON], "has_more": True, "cursor": "next_cur"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            page = orders.list()
        assert page.has_more is True
        assert page.cursor == "next_cur"

    def test_list_orders_with_buyer_email_filter(self, orders):
        page_json = {"data": [ORDER_SUMMARY_JSON], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            list(orders.list(buyer_email="buyer@example.com"))
        assert "buyer_email=buyer%40example.com" in str(
            route.calls[0].request.url
        ) or "buyer_email=buyer@example.com" in str(route.calls[0].request.url)

    def test_list_orders_summary_fields(self, orders):
        page_json = {"data": [ORDER_SUMMARY_JSON], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders").mock(return_value=httpx.Response(200, json=page_json))
            results = list(orders.list())
        item = results[0]
        assert item.listing_id == "lst_abc123"
        assert item.buyer_email == "buyer@example.com"
        assert item.amount == 2999
        assert item.currency == "USD"
        assert item.payment_status == "paid"
        assert item.platform_fee == 0
        assert item.refund_amount == 0


class TestOrderStatus:
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
        assert result.deliverable is not None
        assert result.fulfilled_at is not None


class TestOrderCheckoutData:
    def test_order_with_checkout_data(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_checkout123").mock(
                return_value=httpx.Response(200, json=ORDER_WITH_CHECKOUT_DATA_JSON)
            )
            result = orders.get("ord_checkout123")
        assert result.checkout_data == {"shirt_size": "L", "color": "Blue"}

    def test_order_without_checkout_data(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_9xM4kP7nR2qT5wY1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_9xM4kP7nR2qT5wY1")
        assert result.checkout_data is None


class TestOrderNewFields:
    def test_order_payment_status_and_snapshots(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_9xM4kP7nR2qT5wY1").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            result = orders.get("ord_9xM4kP7nR2qT5wY1")
        assert result.payment_status == "paid"
        assert result.listing_snapshot == {"name": "SEO Playbook", "price": 2999, "slug": "seo-playbook"}
        assert result.seller_snapshot == {"display_name": "Acme Agency"}
        assert result.has_deliverables is False
        assert result.actions is None

    def test_order_metadata_field(self, orders):
        order_with_meta = {**ORDER_JSON, "metadata": {"generated_by": "my-agent", "version": "1"}}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=order_with_meta))
            result = orders.get("ord_1")
        assert result.metadata == {"generated_by": "my-agent", "version": "1"}

    def test_order_actions_list(self, orders):
        order_json = {
            **ORDER_JSON,
            "actions": [
                {
                    "code": "fulfillment_pending",
                    "kind": "api",
                    "priority": "required",
                    "message": "Fulfill this order.",
                    "resolve": {
                        "method": "POST",
                        "endpoint": "/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill",
                        "url": None,
                        "params": None,
                    },
                }
            ],
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/orders/ord_1").mock(return_value=httpx.Response(200, json=order_json))
            result = orders.get("ord_1")
        assert result.actions is not None
        assert len(result.actions) == 1
        assert result.actions[0].code == "fulfillment_pending"
        assert result.actions[0].priority == "required"


class TestFulfillOrder:
    def test_fulfill_order_without_deliverable(self, orders):
        """Close out an external-mode order without pushing content."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            result = orders.fulfill("ord_9xM4kP7nR2qT5wY1")
        assert isinstance(result, OrderResponse)
        assert result.status == "fulfilled"
        body = json.loads(route.calls[0].request.content)
        assert "deliverable" not in body

    def test_fulfill_order_with_text_deliverable(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            result = orders.fulfill(
                "ord_9xM4kP7nR2qT5wY1",
                deliverable=Deliverable.text("Your personalized report..."),
            )
        assert isinstance(result, OrderResponse)
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == {"type": "text", "value": "Your personalized report..."}

    def test_fulfill_order_with_url_deliverable(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            orders.fulfill(
                "ord_9xM4kP7nR2qT5wY1",
                deliverable=Deliverable.url("https://example.com/generated.pdf"),
            )
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == {"type": "url", "value": "https://example.com/generated.pdf"}

    def test_fulfill_order_with_metadata(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            orders.fulfill(
                "ord_9xM4kP7nR2qT5wY1",
                deliverable=Deliverable.text("content"),
                metadata={"generated_by": "my-agent"},
            )
        body = json.loads(route.calls[0].request.content)
        assert body["metadata"] == {"generated_by": "my-agent"}

    def test_fulfill_order_sends_correct_path(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_abc/fulfill").mock(
                return_value=httpx.Response(200, json=FULFILLED_ORDER_JSON)
            )
            orders.fulfill("ord_abc")
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


class TestRedeliverOrder:
    def test_redeliver_returns_redelivery_ack(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/orders/ord_9xM4kP7nR2qT5wY1/redeliver").mock(
                return_value=httpx.Response(200, json=REDELIVER_ACK_JSON)
            )
            result = orders.redeliver("ord_9xM4kP7nR2qT5wY1")
        assert isinstance(result, RedeliveryAck)
        assert result.order_id == "ord_9xM4kP7nR2qT5wY1"
        assert result.scheduled_attempts == 2

    def test_redeliver_sends_correct_path(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/orders/ord_abc/redeliver").mock(
                return_value=httpx.Response(200, json=REDELIVER_ACK_JSON)
            )
            orders.redeliver("ord_abc")
        assert route.called
