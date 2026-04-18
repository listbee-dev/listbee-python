"""Tests for the ApiKeys resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.api_keys import ApiKeys
from listbee.types.api_key import ApiKeyResponse

API_KEY_JSON = {
    "object": "api_key",
    "id": "lbk_7kQ2xY9mN3pR5tW1",
    "name": "Production key",
    "prefix": "lb_pr",
    "last_used_at": "2026-04-17T10:00:00Z",
    "revoked_at": None,
    "created_at": "2026-03-28T12:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def api_keys(sync_client):
    return ApiKeys(sync_client)


class TestSelfRevoke:
    def test_self_revoke_returns_api_key_response(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/api-keys/self-revoke").mock(return_value=httpx.Response(200, json=API_KEY_JSON))
            result = api_keys.self_revoke()
        assert isinstance(result, ApiKeyResponse)
        assert result.id == "lbk_7kQ2xY9mN3pR5tW1"
        assert result.prefix == "lb_pr"

    def test_self_revoke_sends_post_to_correct_endpoint(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/api-keys/self-revoke").mock(return_value=httpx.Response(200, json=API_KEY_JSON))
            api_keys.self_revoke()
        assert route.called

    def test_self_revoke_returns_object_discriminator(self, api_keys):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/api-keys/self-revoke").mock(return_value=httpx.Response(200, json=API_KEY_JSON))
            result = api_keys.self_revoke()
        assert result.object == "api_key"

    def test_self_revoke_without_last_used_at(self, api_keys):
        never_used = {**API_KEY_JSON, "last_used_at": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/api-keys/self-revoke").mock(return_value=httpx.Response(200, json=never_used))
            result = api_keys.self_revoke()
        assert result.last_used_at is None

    def test_self_revoke_with_revoked_at(self, api_keys):
        revoked = {**API_KEY_JSON, "revoked_at": "2026-04-18T09:00:00Z"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/api-keys/self-revoke").mock(return_value=httpx.Response(200, json=revoked))
            result = api_keys.self_revoke()
        assert result.revoked_at is not None
