"""Tests for the Utility resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from listbee._base_client import AsyncClient, SyncClient
from listbee.resources.utility import AsyncUtility, Utility
from listbee.types.plan import PlanListResponse
from listbee.types.utility import PingResponse

PING_JSON = {
    "object": "ping",
    "status": "ok",
}

PLANS_JSON = {
    "object": "list",
    "data": [
        {
            "object": "plan",
            "id": "free",
            "name": "Free",
            "tagline": "Start instantly",
            "price_monthly": 0,
            "fee_rate": "0.10",
        },
        {
            "object": "plan",
            "id": "pro",
            "name": "Pro",
            "tagline": "Scale your sales",
            "price_monthly": 2999,
            "fee_rate": "0.05",
        },
    ],
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


class TestPlans:
    def test_plans_returns_plan_list_response(self, utility):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/plans").mock(return_value=httpx.Response(200, json=PLANS_JSON))
            result = utility.plans()
        assert isinstance(result, PlanListResponse)
        assert result.object == "list"
        assert len(result.data) == 2
        assert result.data[0].id == "free"
        assert result.data[0].name == "Free"
        assert result.data[0].price_monthly == 0
        assert result.data[1].id == "pro"
        assert result.data[1].price_monthly == 2999


class TestAsyncPlans:
    @pytest.mark.asyncio
    async def test_async_plans_returns_plan_list_response(self, async_utility):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/plans").mock(return_value=httpx.Response(200, json=PLANS_JSON))
            result = await async_utility.plans()
        assert isinstance(result, PlanListResponse)
        assert result.object == "list"
        assert len(result.data) == 2
        assert result.data[0].id == "free"
        assert result.data[0].name == "Free"
        assert result.data[0].price_monthly == 0
        assert result.data[1].id == "pro"
        assert result.data[1].price_monthly == 2999
