"""Tests for the Events resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee._pagination import SyncCursorPage
from listbee.resources.events import Events
from listbee.types.event import EventResponse

EVENT_JSON = {
    "object": "event",
    "id": "evt_7kQ2xY9mN3pR5tW1",
    "type": "order.paid",
    "account_id": "acc_7kQ2xY9mN3pR5tW1",
    "listing_id": "lst_abc123",
    "order_id": "ord_9xM4kP7nR2qT5wY1",
    "created_at": "2026-04-18T10:00:00Z",
    "data": {"object": "order", "id": "ord_9xM4kP7nR2qT5wY1", "amount": 2900},
}

EVENT_LIST_JSON = {
    "object": "list",
    "data": [EVENT_JSON],
    "has_more": False,
    "cursor": None,
}

EVENT_LIST_MULTI_PAGE_JSON = {
    "object": "list",
    "data": [EVENT_JSON],
    "has_more": True,
    "cursor": "evt_next_cursor",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def events(sync_client):
    return Events(sync_client)


class TestListEvents:
    def test_list_returns_cursor_page(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            result = events.list()
        assert isinstance(result, SyncCursorPage)
        assert len(result.data) == 1
        assert isinstance(result.data[0], EventResponse)

    def test_list_returns_event_fields(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            result = events.list()
        event = result.data[0]
        assert event.id == "evt_7kQ2xY9mN3pR5tW1"
        assert event.type == "order.paid"
        assert event.account_id == "acc_7kQ2xY9mN3pR5tW1"
        assert event.listing_id == "lst_abc123"
        assert event.order_id == "ord_9xM4kP7nR2qT5wY1"
        assert event.data["amount"] == 2900

    def test_list_filters_by_type(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            events.list(type="order.paid")
        assert route.calls[0].request.url.params["type"] == "order.paid"

    def test_list_filters_by_listing_id(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            events.list(listing_id="lst_abc123")
        assert route.calls[0].request.url.params["listing_id"] == "lst_abc123"

    def test_list_filters_by_order_id(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            events.list(order_id="ord_9xM4kP7nR2qT5wY1")
        assert route.calls[0].request.url.params["order_id"] == "ord_9xM4kP7nR2qT5wY1"

    def test_list_passes_cursor(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            events.list(cursor="evt_cursor_abc")
        assert route.calls[0].request.url.params["cursor"] == "evt_cursor_abc"

    def test_list_passes_limit(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_JSON))
            events.list(limit=5)
        assert route.calls[0].request.url.params["limit"] == "5"

    def test_list_has_more_and_cursor(self, events):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/events").mock(return_value=httpx.Response(200, json=EVENT_LIST_MULTI_PAGE_JSON))
            result = events.list()
        assert result.has_more is True
        assert result.cursor == "evt_next_cursor"

    def test_list_event_with_no_listing_or_order(self, events):
        account_event = {**EVENT_JSON, "type": "listing.created", "listing_id": None, "order_id": None}
        list_json = {**EVENT_LIST_JSON, "data": [account_event]}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/events").mock(return_value=httpx.Response(200, json=list_json))
            result = events.list()
        event = result.data[0]
        assert event.listing_id is None
        assert event.order_id is None
