"""Utility resource — connectivity checks and diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee.types import PingResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Utility:
    """Utility resource for API connectivity and diagnostics."""

    def __init__(self, client: SyncClient) -> None:
        """Initialize Utility resource.

        Args:
            client: The synchronous client instance.
        """
        self._client = client

    def ping(self) -> PingResponse:
        """Check API connectivity and verify the API key is valid.

        Returns:
            A PingResponse with status ok if the API is reachable.

        Example:
            ```python
            response = client.utility.ping()
            print(response.status)  # "ok"
            ```
        """
        response = self._client.get("/v1/ping")
        return PingResponse.model_validate(response.json())


class AsyncUtility:
    """Asynchronous Utility resource for API connectivity and diagnostics."""

    def __init__(self, client: AsyncClient) -> None:
        """Initialize AsyncUtility resource.

        Args:
            client: The asynchronous client instance.
        """
        self._client = client

    async def ping(self) -> PingResponse:
        """Async: Check API connectivity and verify the API key is valid.

        Returns:
            A PingResponse with status ok if the API is reachable.

        Example:
            ```python
            response = await client.utility.ping()
            print(response.status)  # "ok"
            ```
        """
        response = await self._client.get("/v1/ping")
        return PingResponse.model_validate(response.json())
