"""Account resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee.types.account import AccountResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Account:
    """Sync resource for the /v1/account endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def get(self) -> AccountResponse:
        """Retrieve the current account.

        Returns:
            The :class:`~listbee.types.account.AccountResponse` for the
            authenticated account.
        """
        response = self._client.get("/v1/account")
        return AccountResponse.model_validate(response.json())

    def update(self, *, ga_measurement_id: str | None = None) -> AccountResponse:
        """Update account settings.

        Args:
            ga_measurement_id: Google Analytics 4 Measurement ID (e.g. 'G-XXXXXXXXXX').
                Pass ``None`` to clear the existing value.

        Returns:
            The updated :class:`~listbee.types.account.AccountResponse`.
        """
        body: dict[str, Any] = {}
        body["ga_measurement_id"] = ga_measurement_id
        response = self._client.put("/v1/account", json=body)
        return AccountResponse.model_validate(response.json())


class AsyncAccount:
    """Async resource for the /v1/account endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self) -> AccountResponse:
        """Retrieve the current account (async).

        Returns:
            The :class:`~listbee.types.account.AccountResponse` for the
            authenticated account.
        """
        response = await self._client.get("/v1/account")
        return AccountResponse.model_validate(response.json())

    async def update(self, *, ga_measurement_id: str | None = None) -> AccountResponse:
        """Update account settings (async).

        Args:
            ga_measurement_id: Google Analytics 4 Measurement ID (e.g. 'G-XXXXXXXXXX').
                Pass ``None`` to clear the existing value.

        Returns:
            The updated :class:`~listbee.types.account.AccountResponse`.
        """
        body: dict[str, Any] = {}
        body["ga_measurement_id"] = ga_measurement_id
        response = await self._client.put("/v1/account", json=body)
        return AccountResponse.model_validate(response.json())
