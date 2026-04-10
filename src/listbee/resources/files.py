"""Files resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee._raw_response import RawResponse
from listbee.types.file import FileResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient

# Type alias for httpx file tuples: (filename, content, mime_type)
FileUpload = tuple[str, bytes, str]


class _RawFilesProxy:
    """Proxy that calls Files methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def upload(
        self,
        *,
        file: FileUpload,
        purpose: str = "deliverable",
        timeout: float | None = None,
    ) -> RawResponse[FileResponse]:
        """Upload a file and return the raw response."""
        files: dict[str, FileUpload] = {"file": file}
        data: dict[str, str] = {"purpose": purpose}
        response = self._client.post_multipart("/v1/files", files=files, data=data, timeout=timeout)
        return RawResponse(response, FileResponse)


class _AsyncRawFilesProxy:
    """Async proxy that calls Files methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def upload(
        self,
        *,
        file: FileUpload,
        purpose: str = "deliverable",
        timeout: float | None = None,
    ) -> RawResponse[FileResponse]:
        """Upload a file and return the raw response (async)."""
        files: dict[str, FileUpload] = {"file": file}
        data: dict[str, str] = {"purpose": purpose}
        response = await self._client.post_multipart("/v1/files", files=files, data=data, timeout=timeout)
        return RawResponse(response, FileResponse)


class Files:
    """Sync resource for the /v1/files endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawFilesProxy:
        """Access file methods that return raw HTTP responses instead of parsed models."""
        return _RawFilesProxy(self._client)

    def upload(
        self,
        *,
        file: FileUpload,
        purpose: str = "deliverable",
        timeout: float | None = None,
    ) -> FileResponse:
        """Upload a file.

        Returns a file token valid for 24 hours. Pass the token to
        ``listings.set_deliverables()``, ``listings.set_cover()``,
        ``store.set_avatar()``, or ``orders.deliver()`` to attach it.

        Args:
            file: Tuple of (filename, content_bytes, mime_type).
            purpose: File purpose — ``"deliverable"`` (default), ``"cover"``, or ``"avatar"``.
            timeout: Request timeout override. File uploads may take longer.

        Returns:
            The :class:`~listbee.types.file.FileResponse` with a token ID.
        """
        files: dict[str, FileUpload] = {"file": file}
        data: dict[str, str] = {"purpose": purpose}
        response = self._client.post_multipart(
            "/v1/files",
            files=files,
            data=data,
            timeout=timeout,
        )
        return FileResponse.model_validate(response.json())


class AsyncFiles:
    """Async resource for the /v1/files endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawFilesProxy:
        """Access file methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawFilesProxy(self._client)

    async def upload(
        self,
        *,
        file: FileUpload,
        purpose: str = "deliverable",
        timeout: float | None = None,
    ) -> FileResponse:
        """Upload a file (async).

        Returns a file token valid for 24 hours. Pass the token to
        ``listings.set_deliverables()``, ``listings.set_cover()``,
        ``store.set_avatar()``, or ``orders.deliver()`` to attach it.

        Args:
            file: Tuple of (filename, content_bytes, mime_type).
            purpose: File purpose — ``"deliverable"`` (default), ``"cover"``, or ``"avatar"``.
            timeout: Request timeout override. File uploads may take longer.

        Returns:
            The :class:`~listbee.types.file.FileResponse` with a token ID.
        """
        files: dict[str, FileUpload] = {"file": file}
        data: dict[str, str] = {"purpose": purpose}
        response = await self._client.post_multipart(
            "/v1/files",
            files=files,
            data=data,
            timeout=timeout,
        )
        return FileResponse.model_validate(response.json())
