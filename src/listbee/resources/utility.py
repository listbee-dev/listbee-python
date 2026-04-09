"""Utility resource — connectivity checks and diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee._raw_response import RawResponse
from listbee.types import PingResponse, PlanListResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class _RawUtilityProxy:
    """Proxy that calls Utility methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def ping(self) -> RawResponse[PingResponse]:
        """Check API connectivity and return the raw response."""
        response = self._client.request_raw("GET", "/v1/ping")
        return RawResponse(response, PingResponse)

    def plans(self) -> RawResponse[PlanListResponse]:
        """List available pricing plans and return the raw response."""
        response = self._client.request_raw("GET", "/v1/plans")
        return RawResponse(response, PlanListResponse)


class _AsyncRawUtilityProxy:
    """Async proxy that calls Utility methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def ping(self) -> RawResponse[PingResponse]:
        """Check API connectivity and return the raw response (async)."""
        response = await self._client.request_raw("GET", "/v1/ping")
        return RawResponse(response, PingResponse)

    async def plans(self) -> RawResponse[PlanListResponse]:
        """List available pricing plans and return the raw response (async)."""
        response = await self._client.request_raw("GET", "/v1/plans")
        return RawResponse(response, PlanListResponse)


class Utility:
    """Utility resource for API connectivity and diagnostics."""

    def __init__(self, client: SyncClient) -> None:
        """Initialize Utility resource.

        Args:
            client: The synchronous client instance.
        """
        self._client = client

    @property
    def with_raw_response(self) -> _RawUtilityProxy:
        """Access utility methods that return raw HTTP responses instead of parsed models."""
        return _RawUtilityProxy(self._client)

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

    def plans(self) -> PlanListResponse:
        """List all available pricing plans.

        This is a public endpoint — no authentication required.

        Returns:
            A :class:`~listbee.types.plan.PlanListResponse` with all available plans.

        Example:
            ```python
            plans = client.utility.plans()
            for plan in plans.data:
                print(f"{plan.name}: ${plan.price_monthly / 100}")
            ```
        """
        response = self._client.get("/v1/plans")
        return PlanListResponse.model_validate(response.json())


class AsyncUtility:
    """Asynchronous Utility resource for API connectivity and diagnostics."""

    def __init__(self, client: AsyncClient) -> None:
        """Initialize AsyncUtility resource.

        Args:
            client: The asynchronous client instance.
        """
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawUtilityProxy:
        """Access utility methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawUtilityProxy(self._client)

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

    async def plans(self) -> PlanListResponse:
        """List all available pricing plans (async).

        This is a public endpoint — no authentication required.

        Returns:
            A :class:`~listbee.types.plan.PlanListResponse` with all available plans.

        Example:
            ```python
            plans = await client.utility.plans()
            for plan in plans.data:
                print(f"{plan.name}: ${plan.price_monthly / 100}")
            ```
        """
        response = await self._client.get("/v1/plans")
        return PlanListResponse.model_validate(response.json())
