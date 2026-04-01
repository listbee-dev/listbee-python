"""Tests for the Stores resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.stores import Stores
from listbee.types.store import DomainResponse, StoreListResponse, StoreResponse
from listbee.types.stripe import StripeConnectSessionResponse

STORE_JSON = {
    "object": "store",
    "id": "str_7kQ2xY9mN3pR5tW1vB8a",
    "handle": "fitness-brand",
    "name": "Fitness Brand",
    "display_name": "Fitness Brand",
    "bio": None,
    "social_links": [],
    "payment_connected": False,
    "payment_provider": None,
    "currency": None,
    "domain": None,
    "domain_status": None,
    "listing_count": 0,
    "created_at": "2026-03-31T12:00:00Z",
}

STORE_LIST_JSON = {
    "object": "list",
    "data": [STORE_JSON],
}

DOMAIN_JSON = {
    "object": "domain",
    "domain": "fitness.com",
    "status": "pending",
    "cname_target": "buy.listbee.so",
    "verified_at": None,
}

CONNECT_SESSION_JSON = {
    "object": "stripe_connect_session",
    "url": "https://connect.stripe.com/setup/s/abc123",
    "expires_at": "2026-03-31T13:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def stores(sync_client):
    return Stores(sync_client)


class TestCreateStore:
    def test_create_returns_store_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = stores.create(handle="fitness-brand")
        assert isinstance(result, StoreResponse)
        assert result.id == "str_7kQ2xY9mN3pR5tW1vB8a"
        assert result.handle == "fitness-brand"
        assert result.object == "store"

    def test_create_sends_correct_body(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_JSON))
            stores.create(handle="fitness-brand", name="Fitness Brand")
        body = json.loads(route.calls[0].request.content)
        assert body == {"handle": "fitness-brand", "name": "Fitness Brand"}

    def test_create_omits_name_when_none(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_JSON))
            stores.create(handle="fitness-brand")
        body = json.loads(route.calls[0].request.content)
        assert body == {"handle": "fitness-brand"}


class TestListStores:
    def test_list_returns_store_list_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_LIST_JSON))
            result = stores.list()
        assert isinstance(result, StoreListResponse)
        assert len(result.data) == 1
        assert result.data[0].handle == "fitness-brand"


class TestGetStore:
    def test_get_returns_store_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = stores.get("str_7kQ2xY9mN3pR5tW1vB8a")
        assert isinstance(result, StoreResponse)
        assert result.id == "str_7kQ2xY9mN3pR5tW1vB8a"


class TestUpdateStore:
    def test_update_returns_store_response(self, stores):
        updated = {**STORE_JSON, "name": "New Name", "bio": "Great stuff"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.patch("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(return_value=httpx.Response(200, json=updated))
            result = stores.update("str_7kQ2xY9mN3pR5tW1vB8a", name="New Name", bio="Great stuff")
        assert isinstance(result, StoreResponse)
        assert result.name == "New Name"

    def test_update_sends_only_provided_fields(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.patch("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(
                return_value=httpx.Response(200, json=STORE_JSON)
            )
            stores.update("str_7kQ2xY9mN3pR5tW1vB8a", name="New Name")
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "New Name"}
        assert "bio" not in body
        assert "social_links" not in body


class TestDeleteStore:
    def test_delete_sends_request(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(return_value=httpx.Response(204))
            result = stores.delete("str_7kQ2xY9mN3pR5tW1vB8a")
        assert result is None


class TestConnectStripe:
    def test_connect_stripe_returns_session(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/stripe/connect").mock(
                return_value=httpx.Response(200, json=CONNECT_SESSION_JSON)
            )
            result = stores.connect_stripe("str_7kQ2xY9mN3pR5tW1vB8a")
        assert isinstance(result, StripeConnectSessionResponse)
        assert result.url == "https://connect.stripe.com/setup/s/abc123"


class TestSetDomain:
    def test_set_domain_returns_domain_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain").mock(
                return_value=httpx.Response(200, json=DOMAIN_JSON)
            )
            result = stores.set_domain("str_7kQ2xY9mN3pR5tW1vB8a", domain="fitness.com")
        assert isinstance(result, DomainResponse)
        assert result.domain == "fitness.com"
        assert result.status == "pending"
        assert result.cname_target == "buy.listbee.so"

    def test_set_domain_sends_correct_body(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain").mock(
                return_value=httpx.Response(200, json=DOMAIN_JSON)
            )
            stores.set_domain("str_7kQ2xY9mN3pR5tW1vB8a", domain="fitness.com")
        body = json.loads(route.calls[0].request.content)
        assert body == {"domain": "fitness.com"}


class TestVerifyDomain:
    def test_verify_domain_returns_domain_response(self, stores):
        verified = {**DOMAIN_JSON, "status": "verified", "verified_at": "2026-03-31T13:00:00Z"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain/verify").mock(
                return_value=httpx.Response(200, json=verified)
            )
            result = stores.verify_domain("str_7kQ2xY9mN3pR5tW1vB8a")
        assert isinstance(result, DomainResponse)
        assert result.status == "verified"
        assert result.verified_at is not None


class TestRemoveDomain:
    def test_remove_domain_sends_request(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain").mock(return_value=httpx.Response(204))
            result = stores.remove_domain("str_7kQ2xY9mN3pR5tW1vB8a")
        assert result is None
