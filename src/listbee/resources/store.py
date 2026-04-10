"""Store resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee._raw_response import RawResponse
from listbee.types.store import StoreResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class _RawStoreProxy:
    """Proxy that calls Store methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def get(self) -> RawResponse[StoreResponse]:
        """Retrieve the store and return the raw response."""
        response = self._client.request_raw("GET", "/v1/store")
        return RawResponse(response, StoreResponse)


class _AsyncRawStoreProxy:
    """Async proxy that calls Store methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self) -> RawResponse[StoreResponse]:
        """Retrieve the store and return the raw response (async)."""
        response = await self._client.request_raw("GET", "/v1/store")
        return RawResponse(response, StoreResponse)


class Store:
    """Sync resource for the /v1/store endpoint.

    The store holds brand information (display name, slug, bio, avatar) and tracks
    readiness for selling. Brand info moved from Account to Store in the current API version.
    """

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawStoreProxy:
        """Access store methods that return raw HTTP responses instead of parsed models."""
        return _RawStoreProxy(self._client)

    def get(self) -> StoreResponse:
        """Retrieve the current store.

        Returns:
            The :class:`~listbee.types.store.StoreResponse` for the
            authenticated account's store.
        """
        response = self._client.get("/v1/store")
        return StoreResponse.model_validate(response.json())

    def update(
        self,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        avatar_url: str | None = None,
        slug: str | None = None,
    ) -> StoreResponse:
        """Update store settings.

        Args:
            display_name: Store display name shown to buyers.
            bio: Store bio shown on product pages.
            avatar_url: Store avatar image URL.
            slug: URL-safe store slug (3-60 chars, lowercase letters, digits, hyphens).
                Must start and end with alphanumeric characters.

        Returns:
            The updated :class:`~listbee.types.store.StoreResponse`.
        """
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if bio is not None:
            body["bio"] = bio
        if avatar_url is not None:
            body["avatar_url"] = avatar_url
        if slug is not None:
            body["slug"] = slug
        response = self._client.put("/v1/store", json=body)
        return StoreResponse.model_validate(response.json())


class AsyncStore:
    """Async resource for the /v1/store endpoint.

    The store holds brand information (display name, slug, bio, avatar) and tracks
    readiness for selling. Brand info moved from Account to Store in the current API version.
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawStoreProxy:
        """Access store methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawStoreProxy(self._client)

    async def get(self) -> StoreResponse:
        """Retrieve the current store (async).

        Returns:
            The :class:`~listbee.types.store.StoreResponse` for the
            authenticated account's store.
        """
        response = await self._client.get("/v1/store")
        return StoreResponse.model_validate(response.json())

    async def update(
        self,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        avatar_url: str | None = None,
        slug: str | None = None,
    ) -> StoreResponse:
        """Update store settings (async).

        Args:
            display_name: Store display name shown to buyers.
            bio: Store bio shown on product pages.
            avatar_url: Store avatar image URL.
            slug: URL-safe store slug (3-60 chars, lowercase letters, digits, hyphens).
                Must start and end with alphanumeric characters.

        Returns:
            The updated :class:`~listbee.types.store.StoreResponse`.
        """
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if bio is not None:
            body["bio"] = bio
        if avatar_url is not None:
            body["avatar_url"] = avatar_url
        if slug is not None:
            body["slug"] = slug
        response = await self._client.put("/v1/store", json=body)
        return StoreResponse.model_validate(response.json())
