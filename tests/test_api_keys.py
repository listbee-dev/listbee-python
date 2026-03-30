"""Tests for the API Keys resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.api_keys import ApiKeys
from listbee.types.api_key import ApiKeyResponse

API_KEY_JSON = {
    "object": "api_key",
    "id": "lbk_7kQ2xY9mN3pR5tW1",
    "name": "Production",
    "prefix": "lb_prod_",
    "key": None,
    "created_at": "2026-03-30T12:00:00Z",
}

API_KEY_CREATED_JSON = {
    **API_KEY_JSON,
    "key": "lb_prod_a1b2c3d4e5f6g7h8i9j0",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def api_keys(sync_client):
    return ApiKeys(sync_client)


class TestListApiKeys:
    def test_list_returns_list_of_api_key_responses(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/api-keys").mock(
                return_value=httpx.Response(200, json={"data": [API_KEY_JSON]})
            )
            results = api_keys.list()
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], ApiKeyResponse)
        assert results[0].id == "lbk_7kQ2xY9mN3pR5tW1"
        assert results[0].name == "Production"
        assert results[0].key is None

    def test_list_empty(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/api-keys").mock(
                return_value=httpx.Response(200, json={"data": []})
            )
            results = api_keys.list()
        assert results == []


class TestCreateApiKey:
    def test_create_returns_api_key_with_key_value(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/api-keys").mock(
                return_value=httpx.Response(200, json=API_KEY_CREATED_JSON)
            )
            result = api_keys.create(name="Production")
        assert isinstance(result, ApiKeyResponse)
        assert result.id == "lbk_7kQ2xY9mN3pR5tW1"
        assert result.key == "lb_prod_a1b2c3d4e5f6g7h8i9j0"

    def test_create_sends_correct_request_body(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/api-keys").mock(
                return_value=httpx.Response(200, json=API_KEY_CREATED_JSON)
            )
            api_keys.create(name="Production")
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Production"}


class TestDeleteApiKey:
    def test_delete_returns_none(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/api-keys/lbk_7kQ2xY9mN3pR5tW1").mock(
                return_value=httpx.Response(204)
            )
            result = api_keys.delete("lbk_7kQ2xY9mN3pR5tW1")
        assert route.called
        assert result is None
