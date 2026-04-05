"""Signup resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee.types.signup import SignupResponse, VerifyResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Signup:
    """Sync resource for the account signup endpoints."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(self, *, email: str) -> SignupResponse:
        """Initiate a signup by sending an OTP to the given email.

        Args:
            email: The email address to sign up with.

        Returns:
            A :class:`~listbee.types.signup.SignupResponse` confirming the OTP was sent.
        """
        response = self._client.post(
            "/v1/account",
            json={"email": email},
            authenticated=False,
        )
        return SignupResponse.model_validate(response.json())

    def verify(self, *, email: str, code: str) -> VerifyResponse:
        """Verify a signup OTP and create the account.

        Args:
            email: The email address used during signup.
            code: The OTP code received via email.

        Returns:
            A :class:`~listbee.types.signup.VerifyResponse` containing the new
            account and API key.
        """
        response = self._client.post(
            "/v1/account/verify/otp",
            json={"email": email, "code": code},
            authenticated=False,
        )
        return VerifyResponse.model_validate(response.json())


class AsyncSignup:
    """Async resource for the account signup endpoints."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, *, email: str) -> SignupResponse:
        """Initiate a signup by sending an OTP to the given email (async).

        Args:
            email: The email address to sign up with.

        Returns:
            A :class:`~listbee.types.signup.SignupResponse` confirming the OTP was sent.
        """
        response = await self._client.post(
            "/v1/account",
            json={"email": email},
            authenticated=False,
        )
        return SignupResponse.model_validate(response.json())

    async def verify(self, *, email: str, code: str) -> VerifyResponse:
        """Verify a signup OTP and create the account (async).

        Args:
            email: The email address used during signup.
            code: The OTP code received via email.

        Returns:
            A :class:`~listbee.types.signup.VerifyResponse` containing the new
            account and API key.
        """
        response = await self._client.post(
            "/v1/account/verify/otp",
            json={"email": email, "code": code},
            authenticated=False,
        )
        return VerifyResponse.model_validate(response.json())
