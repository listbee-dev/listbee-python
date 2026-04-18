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

    def self_revoke(self) -> RawResponse[ApiKeyResponse]:
        """Self-revoke the current API key and return the raw response."""
        response = self._client.request_raw("POST", "/v1/api-keys/self-revoke")
        return RawResponse(response, ApiKeyResponse)


class _AsyncRawApiKeysProxy:
    """Async proxy that calls ApiKeys methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def self_revoke(self) -> RawResponse[ApiKeyResponse]:
        """Self-revoke the current API key (async) and return the raw response."""
        response = await self._client.request_raw("POST", "/v1/api-keys/self-revoke")
        return RawResponse(response, ApiKeyResponse)


class ApiKeys:
    """Sync resource for the /v1/api-keys endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawApiKeysProxy:
        """Return a proxy that exposes ``RawResponse`` wrappers for each method."""
        return _RawApiKeysProxy(self._client)

    def self_revoke(self) -> ApiKeyResponse:
        """Self-revoke the API key used to make this request.

        Immediately invalidates the current API key. The key cannot be
        used again after this call succeeds. Use this when decommissioning
        an agent or rotating credentials.

        Returns:
            The :class:`~listbee.types.api_key.ApiKeyResponse` with
            ``revoked_at`` set to the current timestamp.
        """
        response = self._client.post("/v1/api-keys/self-revoke")
        return ApiKeyResponse.model_validate(response.json())


class AsyncApiKeys:
    """Async resource for the /v1/api-keys endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawApiKeysProxy:
        """Return an async proxy that exposes ``RawResponse`` wrappers for each method."""
        return _AsyncRawApiKeysProxy(self._client)

    async def self_revoke(self) -> ApiKeyResponse:
        """Self-revoke the API key used to make this request (async).

        Immediately invalidates the current API key. The key cannot be
        used again after this call succeeds. Use this when decommissioning
        an agent or rotating credentials.

        Returns:
            The :class:`~listbee.types.api_key.ApiKeyResponse` with
            ``revoked_at`` set to the current timestamp.
        """
        response = await self._client.post("/v1/api-keys/self-revoke")
        return ApiKeyResponse.model_validate(response.json())
