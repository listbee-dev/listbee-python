"""Tests for the Webhooks resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee._pagination import SyncCursorPage
from listbee.resources.webhooks import Webhooks
from listbee.types.webhook import WebhookEventResponse, WebhookResponse, WebhookTestResponse

WEBHOOK_EVENT_JSON = {
    "object": "webhook_event",
    "id": "evt_7kQ2xY9mN3pR5tW1",
    "event_type": "order.paid",
    "status": "delivered",
    "attempts": 1,
    "max_retries": 5,
    "response_status": 200,
    "last_error": None,
    "created_at": "2026-03-28T12:00:00Z",
    "delivered_at": "2026-03-28T12:00:01Z",
    "failed_at": None,
    "next_retry_at": None,
}

WEBHOOK_TEST_JSON = {
    "object": "webhook_test",
    "success": True,
    "status_code": 200,
    "response_body": "OK",
    "error": None,
}

WEBHOOK_JSON = {
    "object": "webhook",
    "id": "wh_3mK8nP2qR5tW7xY1",
    "name": "Order notifications",
    "url": "https://example.com/webhooks/listbee",
    "secret": "whsec_a1b2c3d4e5f6",
    "events": ["order.paid"],
    "enabled": True,
    "disabled_reason": None,
    "readiness": {"ready": True, "actions": [], "next": None},
    "created_at": "2026-03-28T12:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def webhooks(sync_client):
    return Webhooks(sync_client)


class TestCreateWebhook:
    def test_create_webhook_returns_webhook_response(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/webhooks").mock(return_value=httpx.Response(200, json=WEBHOOK_JSON))
            result = webhooks.create(
                name="Order notifications",
                url="https://example.com/webhooks/listbee",
                events=["order.paid"],
            )
        assert isinstance(result, WebhookResponse)
        assert result.id == "wh_3mK8nP2qR5tW7xY1"
        assert result.name == "Order notifications"
        assert result.url == "https://example.com/webhooks/listbee"
        assert result.events == ["order.paid"]
        assert result.enabled is True

    def test_create_webhook_without_events(self, webhooks):
        no_events_json = {**WEBHOOK_JSON, "events": []}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/webhooks").mock(return_value=httpx.Response(200, json=no_events_json))
            result = webhooks.create(name="All events", url="https://example.com/hooks")
        body = json.loads(route.calls[0].request.content)
        assert "events" not in body
        assert result.events == []


class TestListWebhooks:
    def test_list_webhooks_returns_page(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/webhooks").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [WEBHOOK_JSON],
                        "has_more": False,
                        "cursor": None,
                    },
                )
            )
            page = webhooks.list()
        assert isinstance(page, SyncCursorPage)
        assert len(page.data) == 1
        assert isinstance(page.data[0], WebhookResponse)
        assert page.data[0].id == "wh_3mK8nP2qR5tW7xY1"
        assert page.has_more is False

    def test_list_webhooks_with_limit_parameter(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/webhooks").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [WEBHOOK_JSON],
                        "has_more": False,
                        "cursor": None,
                    },
                )
            )
            webhooks.list(limit=50)
        assert route.called
        assert "limit=50" in str(route.calls[0].request.url)

    def test_list_webhooks_with_cursor_pagination(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/webhooks").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [WEBHOOK_JSON],
                        "has_more": False,
                        "cursor": None,
                    },
                )
            )
            webhooks.list(cursor="wh_cursor_abc")
        assert route.called
        assert "cursor=wh_cursor_abc" in str(route.calls[0].request.url)

    def test_list_webhooks_empty(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/webhooks").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [],
                        "has_more": False,
                        "cursor": None,
                    },
                )
            )
            page = webhooks.list()
        assert isinstance(page, SyncCursorPage)
        assert page.data == []
        assert page.has_more is False


class TestUpdateWebhook:
    def test_update_webhook_returns_updated_response(self, webhooks):
        updated_json = {**WEBHOOK_JSON, "name": "Renamed", "enabled": False}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/webhooks/wh_3mK8nP2qR5tW7xY1").mock(return_value=httpx.Response(200, json=updated_json))
            result = webhooks.update("wh_3mK8nP2qR5tW7xY1", name="Renamed", enabled=False)
        assert isinstance(result, WebhookResponse)
        assert result.name == "Renamed"
        assert result.enabled is False

    def test_update_webhook_only_sends_provided_fields(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/webhooks/wh_3mK8nP2qR5tW7xY1").mock(
                return_value=httpx.Response(200, json=WEBHOOK_JSON)
            )
            webhooks.update("wh_3mK8nP2qR5tW7xY1", name="New name")
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "New name"}
        assert "url" not in body
        assert "events" not in body
        assert "enabled" not in body


class TestDeleteWebhook:
    def test_delete_webhook_sends_delete_request(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/webhooks/wh_3mK8nP2qR5tW7xY1").mock(return_value=httpx.Response(204))
            result = webhooks.delete("wh_3mK8nP2qR5tW7xY1")
        assert route.called
        assert result is None


class TestListWebhookEvents:
    def test_list_events_returns_page(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/webhooks/wh_3mK8nP2qR5tW7xY1/events").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [WEBHOOK_EVENT_JSON],
                        "has_more": False,
                        "total_count": 1,
                        "cursor": None,
                    },
                )
            )
            page = webhooks.list_events("wh_3mK8nP2qR5tW7xY1")
        assert isinstance(page, SyncCursorPage)
        assert len(page.data) == 1
        assert isinstance(page.data[0], WebhookEventResponse)
        assert page.data[0].status == "delivered"
        assert page.has_more is False
        assert page.total_count == 1

    def test_list_events_with_status_filter(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/webhooks/wh_3mK8nP2qR5tW7xY1/events").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [WEBHOOK_EVENT_JSON],
                        "has_more": False,
                        "total_count": 1,
                        "cursor": None,
                    },
                )
            )
            webhooks.list_events("wh_3mK8nP2qR5tW7xY1", status="delivered")
        assert route.called
        assert "status=delivered" in str(route.calls[0].request.url)


class TestWebhookTest:
    def test_webhook(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/webhooks/wh_3mK8nP2qR5tW7xY1/test").mock(
                return_value=httpx.Response(200, json=WEBHOOK_TEST_JSON)
            )
            result = webhooks.test("wh_3mK8nP2qR5tW7xY1")
        assert isinstance(result, WebhookTestResponse)
        assert result.success is True
        assert result.status_code == 200


class TestRetryEvent:
    def test_retry_event_returns_event_response(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/webhooks/wh_abc123/events/evt_def456/retry").mock(
                return_value=httpx.Response(200, json=WEBHOOK_EVENT_JSON)
            )
            result = webhooks.retry_event("wh_abc123", "evt_def456")
        assert isinstance(result, WebhookEventResponse)

    def test_retry_event_sends_correct_path(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/webhooks/wh_abc123/events/evt_def456/retry").mock(
                return_value=httpx.Response(200, json=WEBHOOK_EVENT_JSON)
            )
            webhooks.retry_event("wh_abc123", "evt_def456")
        assert route.called
