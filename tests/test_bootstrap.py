"""Tests for the Bootstrap resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.bootstrap import Bootstrap
from listbee.types.bootstrap import BootstrapCompleteResponse, BootstrapResponse, BootstrapVerifyResponse

BOOTSTRAP_RESPONSE_JSON = {
    "object": "bootstrap_session",
    "session": "sess_abc123",
    "otp_sent": True,
}

BOOTSTRAP_VERIFY_JSON = {
    "object": "bootstrap_session",
    "verified": True,
    "session": "sess_abc123_verified",
}

BOOTSTRAP_COMPLETE_JSON = {
    "object": "bootstrap",
    "account_id": "acc_new1234567890",
    "api_key": "lb_new_apikey_abc123",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def bootstrap(sync_client):
    return Bootstrap(sync_client)


class TestBootstrapStart:
    def test_start_sends_email_and_returns_session(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/bootstrap").mock(return_value=httpx.Response(200, json=BOOTSTRAP_RESPONSE_JSON))
            result = bootstrap.start(email="seller@example.com")
        body = json.loads(route.calls[0].request.content)
        assert body == {"email": "seller@example.com"}
        assert isinstance(result, BootstrapResponse)
        assert result.session == "sess_abc123"
        assert result.otp_sent is True

    def test_start_returns_bootstrap_response(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap").mock(return_value=httpx.Response(200, json=BOOTSTRAP_RESPONSE_JSON))
            result = bootstrap.start(email="test@example.com")
        assert isinstance(result, BootstrapResponse)
        assert result.object == "bootstrap_session"


class TestBootstrapVerify:
    def test_verify_sends_session_and_code(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_JSON))
            result = bootstrap.verify(session="sess_abc123", code="123456")
        body = json.loads(route.calls[0].request.content)
        assert body == {"session": "sess_abc123", "code": "123456"}
        assert isinstance(result, BootstrapVerifyResponse)
        assert result.verified is True
        assert result.session == "sess_abc123_verified"

    def test_verify_returns_bootstrap_verify_response(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_JSON))
            result = bootstrap.verify(session="sess_abc123", code="000000")
        assert isinstance(result, BootstrapVerifyResponse)
        assert result.object == "bootstrap_session"


class TestBootstrapComplete:
    def test_complete_sends_session(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/bootstrap/complete").mock(
                return_value=httpx.Response(201, json=BOOTSTRAP_COMPLETE_JSON)
            )
            result = bootstrap.complete(session="sess_abc123_verified")
        body = json.loads(route.calls[0].request.content)
        assert body == {"session": "sess_abc123_verified"}
        assert isinstance(result, BootstrapCompleteResponse)

    def test_complete_returns_account_id_and_api_key(self, bootstrap):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap/complete").mock(return_value=httpx.Response(201, json=BOOTSTRAP_COMPLETE_JSON))
            result = bootstrap.complete(session="sess_abc123_verified")
        assert isinstance(result, BootstrapCompleteResponse)
        assert result.object == "bootstrap"
        assert result.account_id == "acc_new1234567890"
        assert result.api_key == "lb_new_apikey_abc123"

    def test_full_bootstrap_flow(self, bootstrap):
        """Integration-style test: full 3-step bootstrap flow."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/bootstrap").mock(return_value=httpx.Response(200, json=BOOTSTRAP_RESPONSE_JSON))
            mock.post("/v1/bootstrap/verify").mock(return_value=httpx.Response(200, json=BOOTSTRAP_VERIFY_JSON))
            mock.post("/v1/bootstrap/complete").mock(return_value=httpx.Response(201, json=BOOTSTRAP_COMPLETE_JSON))

            # Step 1: start
            step1 = bootstrap.start(email="seller@example.com")
            assert step1.otp_sent is True

            # Step 2: verify
            step2 = bootstrap.verify(session=step1.session, code="123456")
            assert step2.verified is True

            # Step 3: complete
            result = bootstrap.complete(session=step2.session)
            assert result.api_key == "lb_new_apikey_abc123"
            assert result.account_id == "acc_new1234567890"
