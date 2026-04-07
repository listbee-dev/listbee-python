"""Tests for the Signup resource (send_otp + verify_otp, unauthenticated)."""

from __future__ import annotations

import json

import httpx
import respx

from listbee import ListBee
from listbee.types.signup import AuthSessionResponse, OtpRequestResponse

OTP_REQUEST_RESPONSE = {
    "object": "otp_request",
    "email": "new@example.com",
    "expires_in": 300,
    "message": "Check your email for a 6-digit verification code.",
}

AUTH_SESSION_RESPONSE = {
    "object": "auth_session",
    "access_token": "at_abc123def456",
    "token_type": "bearer",
    "expires_in": 86400,
    "is_new": True,
    "account": {
        "object": "account",
        "id": "acc_7kQ2xY9mN3pR5tW1",
        "email": "new@example.com",
        "plan": "free",
        "fee_rate": "0.10",
        "currency": None,
        "display_name": None,
        "bio": None,
        "has_avatar": False,
        "billing_status": "active",
        "stats": {"total_revenue": 0, "total_orders": 0, "total_listings": 0},
        "readiness": {"operational": False, "actions": [], "next": None},
        "created_at": "2026-03-30T12:00:00Z",
    },
}


class TestSignupSendOtp:
    def test_send_otp_returns_otp_request_response(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/auth/otp").mock(return_value=httpx.Response(200, json=OTP_REQUEST_RESPONSE))
            result = client.signup.send_otp(email="new@example.com")

        assert isinstance(result, OtpRequestResponse)
        assert result.object == "otp_request"
        assert result.email == "new@example.com"
        assert result.expires_in == 300
        assert result.message == "Check your email for a 6-digit verification code."

    def test_send_otp_sends_no_auth_header(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/auth/otp").mock(return_value=httpx.Response(200, json=OTP_REQUEST_RESPONSE))
            client.signup.send_otp(email="new@example.com")

        assert route.called
        sent_headers = route.calls[0].request.headers
        assert "authorization" not in sent_headers

    def test_send_otp_request_body_contains_email(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/auth/otp").mock(return_value=httpx.Response(200, json=OTP_REQUEST_RESPONSE))
            client.signup.send_otp(email="new@example.com")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"email": "new@example.com"}


class TestSignupVerifyOtp:
    def test_verify_otp_returns_auth_session_response(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/auth/otp/verify").mock(return_value=httpx.Response(200, json=AUTH_SESSION_RESPONSE))
            result = client.signup.verify_otp(email="new@example.com", code="123456")

        assert isinstance(result, AuthSessionResponse)
        assert result.object == "auth_session"
        assert result.access_token == "at_abc123def456"
        assert result.token_type == "bearer"
        assert result.expires_in == 86400
        assert result.is_new is True
        assert result.account.id == "acc_7kQ2xY9mN3pR5tW1"
        assert result.account.email == "new@example.com"

    def test_verify_otp_sends_no_auth_header(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/auth/otp/verify").mock(return_value=httpx.Response(200, json=AUTH_SESSION_RESPONSE))
            client.signup.verify_otp(email="new@example.com", code="123456")

        assert route.called
        sent_headers = route.calls[0].request.headers
        assert "authorization" not in sent_headers

    def test_verify_otp_request_body_contains_email_and_code(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/auth/otp/verify").mock(return_value=httpx.Response(200, json=AUTH_SESSION_RESPONSE))
            client.signup.verify_otp(email="new@example.com", code="123456")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"email": "new@example.com", "code": "123456"}

    def test_verify_otp_is_new_false_for_returning_account(self):
        client = ListBee(api_key=None, base_url="https://api.listbee.so")
        returning_response = {**AUTH_SESSION_RESPONSE, "is_new": False}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/auth/otp/verify").mock(return_value=httpx.Response(200, json=returning_response))
            result = client.signup.verify_otp(email="new@example.com", code="123456")

        assert result.is_new is False
