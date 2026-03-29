"""Account resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
