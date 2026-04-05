"""Stripe resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee.types.account import AccountResponse
from listbee.types.stripe import StripeConnectSessionResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Stripe:
    """Sync resource for Stripe-related endpoints."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def connect(self) -> StripeConnectSessionResponse:
        """Create a Stripe Connect onboarding session.

        Returns:
            A :class:`~listbee.types.stripe.StripeConnectSessionResponse` with
            a URL to redirect the user to Stripe's onboarding flow.
        """
        response = self._client.post("/v1/account/stripe/connect")
        return StripeConnectSessionResponse.model_validate(response.json())

    def disconnect(self) -> AccountResponse:
        """Disconnect the Stripe account.

        Returns:
            The updated :class:`~listbee.types.account.AccountResponse`.
        """
        response = self._client.delete("/v1/account/stripe")
        return AccountResponse.model_validate(response.json())


class AsyncStripe:
    """Async resource for Stripe-related endpoints."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def connect(self) -> StripeConnectSessionResponse:
        """Create a Stripe Connect onboarding session (async).

        Returns:
            A :class:`~listbee.types.stripe.StripeConnectSessionResponse` with
            a URL to redirect the user to Stripe's onboarding flow.
        """
        response = await self._client.post("/v1/account/stripe/connect")
        return StripeConnectSessionResponse.model_validate(response.json())

    async def disconnect(self) -> AccountResponse:
        """Disconnect the Stripe account (async).

        Returns:
            The updated :class:`~listbee.types.account.AccountResponse`.
        """
        response = await self._client.delete("/v1/account/stripe")
        return AccountResponse.model_validate(response.json())
