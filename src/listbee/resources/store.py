"""Store resource — sync and async variants."""

from __future__ import annotations

import mimetypes
from typing import TYPE_CHECKING, Any, BinaryIO, cast

from listbee._exceptions import ListBeeError
from listbee._raw_response import RawResponse
from listbee.types.store import StoreResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient

# Accepted image MIME types for avatar uploads
_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}

_MAX_URL_REDIRECTS = 3
_URL_FETCH_TIMEOUT = 30.0


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
        avatar: str | None = None,
        slug: str | None = None,
    ) -> StoreResponse:
        """Update store settings.

        Args:
            display_name: Store display name shown to buyers.
            bio: Store bio shown on product pages.
            avatar: File token for the store avatar image (``file_`` prefixed).
                Upload a file first with ``client.files.upload(purpose="avatar")``
                to get a token, then pass it here. Use :meth:`set_avatar` for a
                one-step helper that handles upload from bytes, BinaryIO, or URL.
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
        if avatar is not None:
            body["avatar"] = avatar
        if slug is not None:
            body["slug"] = slug
        response = self._client.put("/v1/store", json=body)
        return StoreResponse.model_validate(response.json())

    def set_avatar(self, source: str | BinaryIO | bytes) -> StoreResponse:
        """Set the store avatar from a file token, URL, or binary content.

        Accepts three input forms:

        * **File token** (``file_`` prefix) — passed directly to store update.
          Upload via ``client.files.upload(purpose="avatar")`` first.
        * **URL** (``http://`` / ``https://``) — fetched, validated as an image,
          uploaded with ``purpose="avatar"``, then applied.
        * **bytes / BinaryIO** — uploaded with ``purpose="avatar"``, then applied.

        Args:
            source: A ``file_`` token, an image URL, raw bytes, or a file-like object.

        Returns:
            The updated :class:`~listbee.types.store.StoreResponse`.

        Raises:
            ListBeeError: If the URL fetch fails, returns a non-image content type,
                or the upload/update request fails.
        """
        import httpx as _httpx

        token = self._resolve_avatar_source(source, _httpx)
        return self.update(avatar=token)

    def _resolve_avatar_source(self, source: str | BinaryIO | bytes, _httpx: Any) -> str:
        """Upload (if needed) and return a file_ token for the avatar."""
        from listbee.resources.files import Files

        files_resource = Files(self._client)

        if isinstance(source, str) and source.startswith("file_"):
            return source

        if isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
            with _httpx.Client(follow_redirects=True, max_redirects=_MAX_URL_REDIRECTS) as http:
                try:
                    resp = http.get(source, timeout=_URL_FETCH_TIMEOUT)
                except _httpx.TimeoutException as exc:
                    raise ListBeeError(f"Timed out fetching avatar URL: {source}") from exc
                except _httpx.RequestError as exc:
                    raise ListBeeError(f"Failed to fetch avatar URL: {source} — {exc}") from exc
                if resp.is_error:
                    raise ListBeeError(f"Failed to fetch avatar URL: {source} — HTTP {resp.status_code}")
                content_type = resp.headers.get("content-type", "").split(";")[0].strip()
                if content_type not in _IMAGE_MIME_TYPES:
                    raise ListBeeError(f"URL did not return an image (got Content-Type: {content_type}): {source}")
                content = resp.content
                ext = mimetypes.guess_extension(content_type) or ".jpg"
                filename = f"avatar{ext}"
                file_resp = files_resource.upload(file=(filename, content, content_type), purpose="avatar")
                return file_resp.id

        # bytes or BinaryIO
        if isinstance(source, bytes):
            content: bytes = source
            filename = "avatar.jpg"
            content_type = "image/jpeg"
        else:
            content = cast(bytes, source.read())  # type: ignore[union-attr]
            name = getattr(source, "name", "avatar.jpg")
            filename = name if isinstance(name, str) else "avatar.jpg"
            guessed, _ = mimetypes.guess_type(filename)
            content_type = guessed or "image/jpeg"

        file_resp = files_resource.upload(file=(filename, content, content_type), purpose="avatar")
        return file_resp.id


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
        avatar: str | None = None,
        slug: str | None = None,
    ) -> StoreResponse:
        """Update store settings (async).

        Args:
            display_name: Store display name shown to buyers.
            bio: Store bio shown on product pages.
            avatar: File token for the store avatar image (``file_`` prefixed).
                Upload a file first with ``client.files.upload(purpose="avatar")``
                to get a token, then pass it here. Use :meth:`set_avatar` for a
                one-step helper that handles upload from bytes, BinaryIO, or URL.
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
        if avatar is not None:
            body["avatar"] = avatar
        if slug is not None:
            body["slug"] = slug
        response = await self._client.put("/v1/store", json=body)
        return StoreResponse.model_validate(response.json())

    async def set_avatar(self, source: str | BinaryIO | bytes) -> StoreResponse:
        """Set the store avatar from a file token, URL, or binary content (async).

        Accepts three input forms:

        * **File token** (``file_`` prefix) — passed directly to store update.
          Upload via ``client.files.upload(purpose="avatar")`` first.
        * **URL** (``http://`` / ``https://``) — fetched, validated as an image,
          uploaded with ``purpose="avatar"``, then applied.
        * **bytes / BinaryIO** — uploaded with ``purpose="avatar"``, then applied.

        Args:
            source: A ``file_`` token, an image URL, raw bytes, or a file-like object.

        Returns:
            The updated :class:`~listbee.types.store.StoreResponse`.

        Raises:
            ListBeeError: If the URL fetch fails, returns a non-image content type,
                or the upload/update request fails.
        """
        import httpx as _httpx

        token = await self._resolve_avatar_source(source, _httpx)
        return await self.update(avatar=token)

    async def _resolve_avatar_source(self, source: str | BinaryIO | bytes, _httpx: Any) -> str:
        """Upload (if needed) and return a file_ token for the avatar (async)."""
        import mimetypes as _mimetypes

        from listbee.resources.files import AsyncFiles

        files_resource = AsyncFiles(self._client)

        if isinstance(source, str) and source.startswith("file_"):
            return source

        if isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
            async with _httpx.AsyncClient(follow_redirects=True, max_redirects=_MAX_URL_REDIRECTS) as http:
                try:
                    resp = await http.get(source, timeout=_URL_FETCH_TIMEOUT)
                except _httpx.TimeoutException as exc:
                    raise ListBeeError(f"Timed out fetching avatar URL: {source}") from exc
                except _httpx.RequestError as exc:
                    raise ListBeeError(f"Failed to fetch avatar URL: {source} — {exc}") from exc
                if resp.is_error:
                    raise ListBeeError(f"Failed to fetch avatar URL: {source} — HTTP {resp.status_code}")
                content_type = resp.headers.get("content-type", "").split(";")[0].strip()
                if content_type not in _IMAGE_MIME_TYPES:
                    raise ListBeeError(f"URL did not return an image (got Content-Type: {content_type}): {source}")
                content = resp.content
                ext = _mimetypes.guess_extension(content_type) or ".jpg"
                filename = f"avatar{ext}"
                file_resp = await files_resource.upload(file=(filename, content, content_type), purpose="avatar")
                return file_resp.id

        # bytes or BinaryIO
        if isinstance(source, bytes):
            content: bytes = source
            filename = "avatar.jpg"
            content_type = "image/jpeg"
        else:
            content = cast(bytes, source.read())  # type: ignore[union-attr]
            name = getattr(source, "name", "avatar.jpg")
            filename = name if isinstance(name, str) else "avatar.jpg"
            guessed, _ = _mimetypes.guess_type(filename)
            content_type = guessed or "image/jpeg"

        file_resp = await files_resource.upload(file=(filename, content, content_type), purpose="avatar")
        return file_resp.id
