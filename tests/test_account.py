"""Tests for the Account resource."""

from __future__ import annotations

import json

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
    "display_name": "Example Seller",
    "bio": None,
    "has_avatar": False,
    "billing_status": "active",
    "ga_measurement_id": None,
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


class TestUpdateAccount:
    def test_update_account_sets_ga_measurement_id(self, account):
        updated = {**ACCOUNT_JSON, "ga_measurement_id": "G-ABC123XYZ"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/account").mock(return_value=httpx.Response(200, json=updated))
            result = account.update(ga_measurement_id="G-ABC123XYZ")
        body = json.loads(route.calls[0].request.content)
        assert body["ga_measurement_id"] == "G-ABC123XYZ"
        assert isinstance(result, AccountResponse)
        assert result.ga_measurement_id == "G-ABC123XYZ"

    def test_update_account_clears_ga_measurement_id(self, account):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/account").mock(return_value=httpx.Response(200, json=ACCOUNT_JSON))
            result = account.update(ga_measurement_id=None)
        body = json.loads(route.calls[0].request.content)
        assert body["ga_measurement_id"] is None
        assert result.ga_measurement_id is None

    def test_update_account_returns_account_response(self, account):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/account").mock(return_value=httpx.Response(200, json=ACCOUNT_JSON))
            result = account.update()
        assert isinstance(result, AccountResponse)
        assert result.id == "acc_7kQ2xY9mN3pR5tW1"

    def test_get_account_includes_ga_measurement_id_field(self, account):
        with_ga = {**ACCOUNT_JSON, "ga_measurement_id": "G-XXXXXXXXXXX"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/account").mock(return_value=httpx.Response(200, json=with_ga))
            result = account.get()
        assert result.ga_measurement_id == "G-XXXXXXXXXXX"


class TestDeleteAccount:
    def test_delete_account_returns_none(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        account = Account(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/account").mock(return_value=httpx.Response(204))
            result = account.delete()
        assert result is None

    def test_delete_account_sends_delete_request(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        account = Account(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/account").mock(return_value=httpx.Response(204))
            account.delete()
        assert route.called
