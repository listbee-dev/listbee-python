"""Auth resource — send OTP and verify OTP (sync and async variants)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee.types.signup import AuthSessionResponse, OtpRequestResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Signup:
    """Sync resource for the auth endpoints (OTP-based signup and login)."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def send_otp(self, *, email: str) -> OtpRequestResponse:
        """Send a one-time password to the given email address.

        Works for both new and existing accounts. If no account exists for
        this email, one will be created when the code is verified.

        Args:
            email: The email address to send the verification code to.

        Returns:
            An :class:`~listbee.types.signup.OtpRequestResponse` confirming
            the OTP was dispatched.
        """
        response = self._client.post(
            "/v1/auth/otp",
            json={"email": email},
            authenticated=False,
        )
        return OtpRequestResponse.model_validate(response.json())

    def verify_otp(self, *, email: str, code: str) -> AuthSessionResponse:
        """Verify a one-time password and obtain an access token.

        Returns a short-lived access token (24 hours). Use it as a Bearer
        token to create a permanent API key via ``POST /v1/api-keys``.

        Args:
            email: The email address the OTP was sent to.
            code: The 6-digit verification code received via email.

        Returns:
            An :class:`~listbee.types.signup.AuthSessionResponse` containing
            the access token, account details, and whether the account is new.
        """
        response = self._client.post(
            "/v1/auth/otp/verify",
            json={"email": email, "code": code},
            authenticated=False,
        )
        return AuthSessionResponse.model_validate(response.json())


class AsyncSignup:
    """Async resource for the auth endpoints (OTP-based signup and login)."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def send_otp(self, *, email: str) -> OtpRequestResponse:
        """Send a one-time password to the given email address (async).

        Works for both new and existing accounts. If no account exists for
        this email, one will be created when the code is verified.

        Args:
            email: The email address to send the verification code to.

        Returns:
            An :class:`~listbee.types.signup.OtpRequestResponse` confirming
            the OTP was dispatched.
        """
        response = await self._client.post(
            "/v1/auth/otp",
            json={"email": email},
            authenticated=False,
        )
        return OtpRequestResponse.model_validate(response.json())

    async def verify_otp(self, *, email: str, code: str) -> AuthSessionResponse:
        """Verify a one-time password and obtain an access token (async).

        Returns a short-lived access token (24 hours). Use it as a Bearer
        token to create a permanent API key via ``POST /v1/api-keys``.

        Args:
            email: The email address the OTP was sent to.
            code: The 6-digit verification code received via email.

        Returns:
            An :class:`~listbee.types.signup.AuthSessionResponse` containing
            the access token, account details, and whether the account is new.
        """
        response = await self._client.post(
            "/v1/auth/otp/verify",
            json={"email": email, "code": code},
            authenticated=False,
        )
        return AuthSessionResponse.model_validate(response.json())
