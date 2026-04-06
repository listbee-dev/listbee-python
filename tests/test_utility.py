"""Tests for the Utility resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from listbee._base_client import AsyncClient, SyncClient
from listbee.resources.utility import AsyncUtility, Utility
from listbee.types.utility import PingResponse

PING_JSON = {
    "object": "ping",
    "status": "ok",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def async_client():
    return AsyncClient(api_key="lb_test")


@pytest.fixture
def utility(sync_client):
    return Utility(sync_client)


@pytest.fixture
def async_utility(async_client):
    return AsyncUtility(async_client)


class TestPing:
    def test_ping_returns_ping_response(self, utility):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/ping").mock(return_value=httpx.Response(200, json=PING_JSON))
            result = utility.ping()
        assert isinstance(result, PingResponse)
        assert result.object == "ping"
        assert result.status == "ok"


class TestAsyncPing:
    @pytest.mark.asyncio
    async def test_async_ping_returns_ping_response(self, async_utility):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/ping").mock(return_value=httpx.Response(200, json=PING_JSON))
            result = await async_utility.ping()
        assert isinstance(result, PingResponse)
        assert result.object == "ping"
        assert result.status == "ok"
