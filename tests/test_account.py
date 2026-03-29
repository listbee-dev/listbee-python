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
    "readiness": {"operational": True, "blockers": []},
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
        assert result.readiness.operational is True
        assert result.readiness.blockers == []

    def test_get_account_with_blockers(self, account):
        json_with_blockers = {
            **ACCOUNT_JSON,
            "readiness": {
                "operational": False,
                "blockers": [
                    {
                        "code": "payments_not_configured",
                        "message": "Connect a Stripe account to accept payments",
                        "resolve": {
                            "action": "connect_stripe",
                            "url": "https://listbee.so/connect/stripe",
                        },
                    }
                ],
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/account").mock(return_value=httpx.Response(200, json=json_with_blockers))
            result = account.get()
        assert result.readiness.operational is False
        assert len(result.readiness.blockers) == 1
        assert result.readiness.blockers[0].code == "payments_not_configured"
        assert result.readiness.blockers[0].resolve.action == "connect_stripe"
        assert result.readiness.blockers[0].resolve.url == "https://listbee.so/connect/stripe"
