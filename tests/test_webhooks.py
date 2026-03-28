"""Tests for the Webhooks resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.webhooks import Webhooks
from listbee.types.webhook import WebhookResponse

WEBHOOK_JSON = {
    "object": "webhook",
    "id": "wh_3mK8nP2qR5tW7xY1",
    "name": "Order notifications",
    "url": "https://example.com/webhooks/listbee",
    "secret": "whsec_a1b2c3d4e5f6",
    "events": ["order.completed"],
    "enabled": True,
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
                events=["order.completed"],
            )
        assert isinstance(result, WebhookResponse)
        assert result.id == "wh_3mK8nP2qR5tW7xY1"
        assert result.name == "Order notifications"
        assert result.url == "https://example.com/webhooks/listbee"
        assert result.events == ["order.completed"]
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
    def test_list_webhooks_returns_list(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/webhooks").mock(return_value=httpx.Response(200, json={"data": [WEBHOOK_JSON]}))
            results = webhooks.list()
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], WebhookResponse)
        assert results[0].id == "wh_3mK8nP2qR5tW7xY1"

    def test_list_webhooks_falls_back_to_items_key(self, webhooks):
        """Backwards compatibility: if 'data' key is absent, try 'items'."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/webhooks").mock(return_value=httpx.Response(200, json={"items": [WEBHOOK_JSON]}))
            results = webhooks.list()
        assert len(results) == 1
        assert results[0].id == "wh_3mK8nP2qR5tW7xY1"

    def test_list_webhooks_empty(self, webhooks):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/webhooks").mock(return_value=httpx.Response(200, json={"data": []}))
            results = webhooks.list()
        assert results == []


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
