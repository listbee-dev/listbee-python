"""Tests for the Store resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.store import Store
from listbee.types.store import StoreReadiness, StoreResponse

STORE_JSON = {
    "object": "store",
    "id": "st_7kQ2xY9mN3pR5tW1vB8a",
    "display_name": "Acme Agency",
    "slug": "acme-agency",
    "bio": "We make great things.",
    "avatar_url": None,
    "url": "https://buy.listbee.so/acme-agency",
    "api_key": None,
    "readiness": {
        "sellable": True,
        "actions": [],
        "next": None,
    },
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def store(sync_client):
    return Store(sync_client)


class TestGetStore:
    def test_get_returns_store_response(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.get()
        assert isinstance(result, StoreResponse)
        assert result.id == "st_7kQ2xY9mN3pR5tW1vB8a"
        assert result.display_name == "Acme Agency"
        assert result.slug == "acme-agency"
        assert result.bio == "We make great things."
        assert result.avatar_url is None
        assert result.url == "https://buy.listbee.so/acme-agency"
        assert result.api_key is None

    def test_get_store_readiness_sellable(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.get()
        assert isinstance(result.readiness, StoreReadiness)
        assert result.readiness.sellable is True
        assert result.readiness.actions == []
        assert result.readiness.next is None

    def test_get_store_readiness_not_sellable_with_actions(self, store):
        store_with_actions = {
            **STORE_JSON,
            "readiness": {
                "sellable": False,
                "actions": [
                    {
                        "code": "connect_stripe",
                        "kind": "human",
                        "message": "Connect a Stripe account to accept payments",
                        "resolve": {
                            "method": "GET",
                            "endpoint": None,
                            "url": "https://listbee.so/connect/stripe",
                            "params": None,
                        },
                    }
                ],
                "next": "connect_stripe",
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=store_with_actions))
            result = store.get()
        assert result.readiness.sellable is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "connect_stripe"
        assert result.readiness.next == "connect_stripe"


class TestUpdateStore:
    def test_update_display_name(self, store):
        updated = {**STORE_JSON, "display_name": "New Agency Name"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(display_name="New Agency Name")
        body = json.loads(route.calls[0].request.content)
        assert body["display_name"] == "New Agency Name"
        assert isinstance(result, StoreResponse)
        assert result.display_name == "New Agency Name"

    def test_update_bio(self, store):
        updated = {**STORE_JSON, "bio": "New bio text"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(bio="New bio text")
        body = json.loads(route.calls[0].request.content)
        assert body["bio"] == "New bio text"
        assert result.bio == "New bio text"

    def test_update_slug(self, store):
        updated = {**STORE_JSON, "slug": "new-slug"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(slug="new-slug")
        body = json.loads(route.calls[0].request.content)
        assert body["slug"] == "new-slug"
        assert result.slug == "new-slug"

    def test_update_omits_unset_fields(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            store.update(display_name="Only Name")
        body = json.loads(route.calls[0].request.content)
        assert "bio" not in body
        assert "avatar_url" not in body
        assert "slug" not in body

    def test_update_returns_store_response(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.update()
        assert isinstance(result, StoreResponse)
