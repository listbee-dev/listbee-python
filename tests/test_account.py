"""Tests for the Account resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.account import Account
from listbee.types.account import AccountResponse

ACCOUNT_JSON = {
    "object": "account",
    "id": "acc_7kQ2xY9mN3pR5tW1",
    "email": "seller@example.com",
    "plan": "free",
    "fee_rate": "0.10",
    "currency": "USD",
    "stats": {"total_revenue": 125000, "total_orders": 47, "total_listings": 5},
    "readiness": {"operational": True, "actions": [], "next": None},
    "created_at": "2026-03-28T12:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def account(sync_client):
    return Account(sync_client)


class TestGetAccount:
    def test_get_account_returns_account_response(self, account):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/account").mock(return_value=httpx.Response(200, json=ACCOUNT_JSON))
            result = account.get()
        assert isinstance(result, AccountResponse)
        assert result.id == "acc_7kQ2xY9mN3pR5tW1"
        assert result.email == "seller@example.com"
        assert result.plan == "free"
        assert result.fee_rate == "0.10"
        assert result.currency == "USD"
        assert result.stats.total_revenue == 125000
        assert result.stats.total_orders == 47
        assert result.stats.total_listings == 5
        assert result.readiness.operational is True
        assert result.readiness.actions == []

    def test_get_account_with_actions(self, account):
        json_with_actions = {
            **ACCOUNT_JSON,
            "readiness": {
                "operational": False,
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
            mock.get("/v1/account").mock(return_value=httpx.Response(200, json=json_with_actions))
            result = account.get()
        assert result.readiness.operational is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "connect_stripe"
        assert result.readiness.actions[0].kind == "human"
        assert result.readiness.actions[0].resolve.url == "https://listbee.so/connect/stripe"
        assert result.readiness.next == "connect_stripe"
