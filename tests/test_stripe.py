"""Tests for the Stripe resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.stripe import Stripe
from listbee.types.account import AccountResponse
from listbee.types.stripe import StripeConnectSessionResponse

ACCOUNT_RESPONSE = {
    "object": "account",
    "id": "acc_7kQ2xY9mN3pR5tW1",
    "email": "seller@example.com",
    "plan": "free",
    "fee_rate": "0.10",
    "readiness": {"operational": True, "actions": [], "next": None},
    "created_at": "2026-03-30T12:00:00Z",
}

CONNECT_SESSION_RESPONSE = {
    "object": "stripe_connect_session",
    "url": "https://connect.stripe.com/setup/s/abc123",
    "expires_at": "2026-03-30T13:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def stripe(sync_client):
    return Stripe(sync_client)


class TestSetKey:
    def test_set_key_returns_account_response(self, stripe):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/account/stripe-key").mock(
                return_value=httpx.Response(200, json=ACCOUNT_RESPONSE)
            )
            result = stripe.set_key(secret_key="sk_live_abc123")
        assert isinstance(result, AccountResponse)
        assert result.id == "acc_7kQ2xY9mN3pR5tW1"

    def test_set_key_sends_correct_body(self, stripe):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/account/stripe-key").mock(
                return_value=httpx.Response(200, json=ACCOUNT_RESPONSE)
            )
            stripe.set_key(secret_key="sk_live_abc123")
        body = json.loads(route.calls[0].request.content)
        assert body == {"secret_key": "sk_live_abc123"}


class TestConnect:
    def test_connect_returns_stripe_connect_session(self, stripe):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/account/stripe/connect").mock(
                return_value=httpx.Response(200, json=CONNECT_SESSION_RESPONSE)
            )
            result = stripe.connect()
        assert isinstance(result, StripeConnectSessionResponse)
        assert result.url == "https://connect.stripe.com/setup/s/abc123"


class TestDisconnect:
    def test_disconnect_returns_account_response(self, stripe):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/account/stripe").mock(
                return_value=httpx.Response(200, json=ACCOUNT_RESPONSE)
            )
            result = stripe.disconnect()
        assert isinstance(result, AccountResponse)
        assert result.id == "acc_7kQ2xY9mN3pR5tW1"
