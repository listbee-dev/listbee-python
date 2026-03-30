"""Tests for the Orders resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.orders import Orders
from listbee.types.order import OrderResponse

ORDER_JSON = {
    "object": "order",
    "id": "ord_9xM4kP7nR2qT5wY1",
    "listing_id": "lst_abc123",
    "buyer_email": "buyer@example.com",
    "amount": 2999,
    "currency": "USD",
    "stripe_session_id": "cs_test_a1b2c3d4",
    "stripe_payment_intent_id": "pi_3abc123def456",
    "status": "completed",
    "created_at": "2026-03-28T12:00:00Z",
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
        assert result.status == "completed"

    def test_get_order_sends_correct_path(self, orders):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/orders/ord_abc").mock(return_value=httpx.Response(200, json=ORDER_JSON))
            orders.get("ord_abc")
        assert route.called


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
            list(orders.list(status="completed"))
        assert "status=completed" in str(route.calls[0].request.url)

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
