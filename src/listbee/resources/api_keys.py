"""API Keys resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee._raw_response import RawResponse
from listbee.types.api_key import ApiKeyResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class _RawApiKeysProxy:
    """Proxy that calls ApiKeys methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(self, *, name: str) -> RawResponse[ApiKeyResponse]:
        """Create an API key and return the raw response."""
        response = self._client.request_raw("POST", "/v1/api-keys", json={"name": name})
        return RawResponse(response, ApiKeyResponse)


class _AsyncRawApiKeysProxy:
    """Async proxy that calls ApiKeys methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, *, name: str) -> RawResponse[ApiKeyResponse]:
        """Create an API key and return the raw response (async)."""
        response = await self._client.request_raw("POST", "/v1/api-keys", json={"name": name})
        return RawResponse(response, ApiKeyResponse)


class ApiKeys:
    """Sync resource for the /v1/api-keys endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawApiKeysProxy:
        """Access API key methods that return raw HTTP responses instead of parsed models."""
        return _RawApiKeysProxy(self._client)

    def list(self) -> list[ApiKeyResponse]:
        """Return all API keys for the account.

        Returns:
            A list of :class:`~listbee.types.api_key.ApiKeyResponse` objects.
            The ``key`` field is ``None`` in list responses.
        """
        response = self._client.get("/v1/api-keys")
        items = response.json().get("data", [])
        return [ApiKeyResponse.model_validate(item) for item in items]

    def create(self, *, name: str) -> ApiKeyResponse:
        """Create a new API key.

        Args:
            name: Display name for the API key.

        Returns:
            The created :class:`~listbee.types.api_key.ApiKeyResponse`.
            The ``key`` field contains the full key value — store it securely,
            as it will not be shown again.
        """
        response = self._client.post("/v1/api-keys", json={"name": name})
        return ApiKeyResponse.model_validate(response.json())

    def delete(self, key_id: str) -> None:
        """Delete an API key.

        Args:
            key_id: The API key's unique identifier (e.g. "lbk_abc123").
        """
        self._client.delete(f"/v1/api-keys/{key_id}")


class AsyncApiKeys:
    """Async resource for the /v1/api-keys endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawApiKeysProxy:
        """Access API key methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawApiKeysProxy(self._client)

    async def list(self) -> list[ApiKeyResponse]:
        """Return all API keys for the account (async).

        Returns:
            A list of :class:`~listbee.types.api_key.ApiKeyResponse` objects.
            The ``key`` field is ``None`` in list responses.
        """
        response = await self._client.get("/v1/api-keys")
        items = response.json().get("data", [])
        return [ApiKeyResponse.model_validate(item) for item in items]

    async def create(self, *, name: str) -> ApiKeyResponse:
        """Create a new API key (async).

        Args:
            name: Display name for the API key.

        Returns:
            The created :class:`~listbee.types.api_key.ApiKeyResponse`.
            The ``key`` field contains the full key value — store it securely,
            as it will not be shown again.
        """
        response = await self._client.post("/v1/api-keys", json={"name": name})
        return ApiKeyResponse.model_validate(response.json())

    async def delete(self, key_id: str) -> None:
        """Delete an API key (async).

        Args:
            key_id: The API key's unique identifier (e.g. "lbk_abc123").
        """
        await self._client.delete(f"/v1/api-keys/{key_id}")
