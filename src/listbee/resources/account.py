"""Account resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee._raw_response import RawResponse
from listbee.types.account import AccountResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class _RawAccountProxy:
    """Proxy that calls Account methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def get(self) -> RawResponse[AccountResponse]:
        """Retrieve the current account and return the raw response."""
        response = self._client.request_raw("GET", "/v1/account")
        return RawResponse(response, AccountResponse)


class _AsyncRawAccountProxy:
    """Async proxy that calls Account methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self) -> RawResponse[AccountResponse]:
        """Retrieve the current account and return the raw response (async)."""
        response = await self._client.request_raw("GET", "/v1/account")
        return RawResponse(response, AccountResponse)


class Account:
    """Sync resource for the /v1/account endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawAccountProxy:
        """Access account methods that return raw HTTP responses instead of parsed models."""
        return _RawAccountProxy(self._client)

    def get(self) -> AccountResponse:
        """Retrieve the current account.

        Returns:
            The :class:`~listbee.types.account.AccountResponse` for the
            authenticated account.
        """
        response = self._client.get("/v1/account")
        return AccountResponse.model_validate(response.json())

    def delete(self) -> None:
        """Delete the authenticated account.

        This is irreversible. All listings, orders, and webhooks are deleted.
        """
        self._client.delete("/v1/account")

    def update(
        self,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        avatar: str | None = None,
        ga_measurement_id: str | None = None,
        notify_orders: bool | None = None,
    ) -> AccountResponse:
        """Update account settings.

        Args:
            display_name: Public display name shown on the storefront.
            bio: Short seller bio shown on the storefront.
            avatar: URL of an avatar image to fetch and store.
            ga_measurement_id: Google Analytics 4 Measurement ID (e.g. 'G-XXXXXXXXXX').
                Pass ``None`` to clear the existing value.
            notify_orders: Whether to receive email notifications for new orders.

        Returns:
            The updated :class:`~listbee.types.account.AccountResponse`.
        """
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if bio is not None:
            body["bio"] = bio
        if avatar is not None:
            body["avatar"] = avatar
        body["ga_measurement_id"] = ga_measurement_id
        if notify_orders is not None:
            body["notify_orders"] = notify_orders
        response = self._client.put("/v1/account", json=body)
        return AccountResponse.model_validate(response.json())


class AsyncAccount:
    """Async resource for the /v1/account endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawAccountProxy:
        """Access account methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawAccountProxy(self._client)

    async def get(self) -> AccountResponse:
        """Retrieve the current account (async).

        Returns:
            The :class:`~listbee.types.account.AccountResponse` for the
            authenticated account.
        """
        response = await self._client.get("/v1/account")
        return AccountResponse.model_validate(response.json())

    async def delete(self) -> None:
        """Delete the authenticated account (async).

        This is irreversible. All listings, orders, and webhooks are deleted.
        """
        await self._client.delete("/v1/account")

    async def update(
        self,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        avatar: str | None = None,
        ga_measurement_id: str | None = None,
        notify_orders: bool | None = None,
    ) -> AccountResponse:
        """Update account settings (async).

        Args:
            display_name: Public display name shown on the storefront.
            bio: Short seller bio shown on the storefront.
            avatar: URL of an avatar image to fetch and store.
            ga_measurement_id: Google Analytics 4 Measurement ID (e.g. 'G-XXXXXXXXXX').
                Pass ``None`` to clear the existing value.
            notify_orders: Whether to receive email notifications for new orders.

        Returns:
            The updated :class:`~listbee.types.account.AccountResponse`.
        """
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if bio is not None:
            body["bio"] = bio
        if avatar is not None:
            body["avatar"] = avatar
        body["ga_measurement_id"] = ga_measurement_id
        if notify_orders is not None:
            body["notify_orders"] = notify_orders
        response = await self._client.put("/v1/account", json=body)
        return AccountResponse.model_validate(response.json())
