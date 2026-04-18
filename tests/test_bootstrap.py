"""Tests for the Bootstrap resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.bootstrap import Bootstrap
from listbee.types.bootstrap import BootstrapPollResponse, BootstrapStartResponse, BootstrapVerifyResponse

ACCOUNT_READINESS_OPERATIONAL = {"operational": True, "actions": [], "next": None}
ACCOUNT_READINESS_PENDING = {
    "operational": False,
    "actions": [
        {
            "code": "stripe_connect_required",
            "kind": "human",
            "message": "Complete Stripe Connect onboarding",
            "resolve": {
                "method": "GET",
                "endpoint": None,
                "url": "https://connect.stripe.com/setup/e/acct_...",
                "params": None,
            },
        }
    ],
    "next": "stripe_connect_required",
}

BOOTSTRAP_START_JSON = {
    "object": "bootstrap_session",
    "bootstrap_token": "bst_abc123def456",
    "account_id": "acc_new1234567890",
    "otp_expires_at": "2026-04-18T12:10:00Z",
}

BOOTSTRAP_VERIFY_JSON = {
    "object": "bootstrap",
    "account_id": "acc_new1234567890",
    "api_key": "lb_new_apikey_abc123",
    "stripe_onboarding_url": "https://connect.stripe.com/setup/e/acct_...",
    "readiness": ACCOUNT_READINESS_PENDING,
}

BOOTSTRAP_VERIFY_READY_JSON = {
    "object": "bootstrap",
    "account_id": "acc_new1234567890",
    "api_key": "lb_new_apikey_abc123",
    "stripe_onboarding_url": None,
    "readiness": ACCOUNT_READINESS_OPERATIONAL,
}

BOOTSTRAP_POLL_JSON = {
    "object": "bootstrap_poll",
    "ready": False,
    "account_id": "acc_new1234567890",
    "readiness": ACCOUNT_READINESS_PENDING,
    "stripe_onboarding_url": "https://connect.stripe.com/setup/e/acct_...",
}

BOOTSTRAP_POLL_READY_JSON = {
    "object": "bootstrap_poll",
    "ready": True,
    "account_id": "acc_new1234567890",
    "readiness": ACCOUNT_READINESS_OPERATIONAL,
    "stripe_onboarding_url": None,
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def bootstrap(sync_client):
    return Bootstrap(sync_client)


class TestBootstrapStart:
    def test_start_sends_email_and_returns_token(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/bootstrap/start").mock(return_value=httpx.Response(202, json=BOOTSTRAP_START_JSON))
            result = bootstrap.start(email="seller@example.com")
        body = json.loads(route.calls[0].request.content)
        assert body == {"email": "seller@example.com"}
        assert isinstance(result, BootstrapStartResponse)
        assert result.bootstrap_token == "bst_abc123def456"
        assert result.account_id == "acc_new1234567890"

    def test_start_returns_bootstrap_start_response(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/start").mock(return_value=httpx.Response(202, json=BOOTSTRAP_START_JSON))
            result = bootstrap.start(email="test@example.com")
        assert isinstance(result, BootstrapStartResponse)
        assert result.object == "bootstrap_session"
        assert result.otp_expires_at == "2026-04-18T12:10:00Z"


class TestBootstrapVerify:
    def test_verify_sends_bootstrap_token_and_otp_code(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_JSON))
            result = bootstrap.verify(bootstrap_token="bst_abc123def456", otp_code="123456")
        body = json.loads(route.calls[0].request.content)
        assert body == {"bootstrap_token": "bst_abc123def456", "otp_code": "123456"}
        assert isinstance(result, BootstrapVerifyResponse)
        assert result.api_key == "lb_new_apikey_abc123"
        assert result.account_id == "acc_new1234567890"
        assert result.stripe_onboarding_url is not None
        assert result.readiness.operational is False

    def test_verify_returns_api_key_and_readiness(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_READY_JSON))
            result = bootstrap.verify(bootstrap_token="bst_abc123def456", otp_code="000000")
        assert isinstance(result, BootstrapVerifyResponse)
        assert result.object == "bootstrap"
        assert result.api_key == "lb_new_apikey_abc123"
        assert result.readiness.operational is True
        assert result.stripe_onboarding_url is None


class TestBootstrapPoll:
    def test_poll_returns_not_ready(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/bootstrap/acc_new1234567890").mock(return_value=httpx.Response(200, json=BOOTSTRAP_POLL_JSON))
            result = bootstrap.poll("acc_new1234567890")
        assert isinstance(result, BootstrapPollResponse)
        assert result.ready is False
        assert result.account_id == "acc_new1234567890"
        assert result.readiness.operational is False
        assert result.stripe_onboarding_url is not None

    def test_poll_returns_ready(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/bootstrap/acc_new1234567890").mock(
                return_value=httpx.Response(200, json=BOOTSTRAP_POLL_READY_JSON)
            )
            result = bootstrap.poll("acc_new1234567890")
        assert isinstance(result, BootstrapPollResponse)
        assert result.ready is True
        assert result.readiness.operational is True
        assert result.stripe_onboarding_url is None


class TestBootstrapRun:
    def test_run_returns_api_key_when_already_ready(self, bootstrap):
        """If readiness.operational is True after verify, skip polling."""
        otp_calls: list[str] = []

        def fake_otp() -> str:
            otp_calls.append("called")
            return "123456"

        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/start").mock(return_value=httpx.Response(202, json=BOOTSTRAP_START_JSON))
            mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_READY_JSON))
            result = bootstrap.run("seller@example.com", on_otp=fake_otp)

        assert result == "lb_new_apikey_abc123"
        assert otp_calls == ["called"]

    def test_run_calls_on_human_action_with_stripe_url(self, bootstrap):
        """on_human_action is called with stripe_onboarding_url when present."""
        human_action_urls: list[str] = []

        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/start").mock(return_value=httpx.Response(202, json=BOOTSTRAP_START_JSON))
            mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_JSON))
            mock.get("/v1/bootstrap/acc_new1234567890").mock(
                return_value=httpx.Response(200, json=BOOTSTRAP_POLL_READY_JSON)
            )
            result = bootstrap.run(
                "seller@example.com",
                on_otp=lambda: "123456",
                on_human_action=lambda url: human_action_urls.append(url),
                poll_interval=0.0,
            )

        assert result == "lb_new_apikey_abc123"
        assert len(human_action_urls) == 1
        assert "connect.stripe.com" in human_action_urls[0]

    def test_full_bootstrap_flow(self, bootstrap):
        """Integration-style test: full 2-step bootstrap flow."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/start").mock(return_value=httpx.Response(202, json=BOOTSTRAP_START_JSON))
            mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_READY_JSON))

            # Step 1: start
            step1 = bootstrap.start(email="seller@example.com")
            assert step1.bootstrap_token == "bst_abc123def456"
            assert step1.account_id == "acc_new1234567890"

            # Step 2: verify
            step2 = bootstrap.verify(bootstrap_token=step1.bootstrap_token, otp_code="123456")
            assert step2.api_key == "lb_new_apikey_abc123"
            assert step2.account_id == "acc_new1234567890"
            assert step2.readiness.operational is True
