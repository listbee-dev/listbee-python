"""Tests for the Signup resource (create + verify, unauthenticated)."""

from __future__ import annotations

import json

import httpx
import respx

from listbee import ListBee
from listbee.types.signup import SignupResponse, VerifyResponse

SIGNUP_RESPONSE = {
    "object": "signup_session",
    "email": "new@example.com",
    "status": "otp_sent",
    "message": "Check your email for a verification code.",
}

VERIFY_RESPONSE = {
    "object": "signup_result",
    "account": {
        "object": "account",
        "id": "acc_7kQ2xY9mN3pR5tW1",
        "email": "new@example.com",
        "plan": "free",
        "fee_rate": "0.10",
        "readiness": {"operational": False, "actions": [], "next": None},
        "created_at": "2026-03-30T12:00:00Z",
    },
    "api_key": "lb_new_key_abc123",
}


class TestSignupCreate:
    def test_create_returns_signup_response(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/account/signup").mock(
                return_value=httpx.Response(200, json=SIGNUP_RESPONSE)
            )
            result = client.signup.create(email="new@example.com")

        assert isinstance(result, SignupResponse)
        assert result.object == "signup_session"
        assert result.email == "new@example.com"
        assert result.status == "otp_sent"
        assert result.message == "Check your email for a verification code."

    def test_create_sends_no_auth_header(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/account/signup").mock(
                return_value=httpx.Response(200, json=SIGNUP_RESPONSE)
            )
            client.signup.create(email="new@example.com")

        assert route.called
        sent_headers = route.calls[0].request.headers
        assert "authorization" not in sent_headers


class TestSignupVerify:
    def test_verify_returns_verify_response(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/account/verify").mock(
                return_value=httpx.Response(200, json=VERIFY_RESPONSE)
            )
            result = client.signup.verify(email="new@example.com", code="123456")

        assert isinstance(result, VerifyResponse)
        assert result.object == "signup_result"
        assert result.account.id == "acc_7kQ2xY9mN3pR5tW1"
        assert result.account.email == "new@example.com"
        assert result.api_key == "lb_new_key_abc123"

    def test_verify_sends_no_auth_header(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/account/verify").mock(
                return_value=httpx.Response(200, json=VERIFY_RESPONSE)
            )
            client.signup.verify(email="new@example.com", code="123456")

        assert route.called
        sent_headers = route.calls[0].request.headers
        assert "authorization" not in sent_headers

    def test_verify_request_body_contains_email_and_code(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/account/verify").mock(
                return_value=httpx.Response(200, json=VERIFY_RESPONSE)
            )
            client.signup.verify(email="new@example.com", code="123456")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"email": "new@example.com", "code": "123456"}
