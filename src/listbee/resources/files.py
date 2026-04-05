"""Files resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee.types.file import FileResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient

# Type alias for httpx file tuples: (filename, content, mime_type)
FileUpload = tuple[str, bytes, str]


class Files:
    """Sync resource for the /v1/files endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def upload(
        self,
        *,
        file: FileUpload,
        timeout: float | None = None,
    ) -> FileResponse:
        """Upload a file for use as a listing deliverable.

        Returns a file token valid for 24 hours. Pass the token to
        ``listings.set_deliverables()`` or ``orders.deliver()`` to attach it.

        Args:
            file: Tuple of (filename, content_bytes, mime_type).
            timeout: Request timeout override. File uploads may take longer.

        Returns:
            The :class:`~listbee.types.file.FileResponse` with a token ID.
        """
        response = self._client.post_multipart(
            "/v1/files",
            files={"file": file},
            timeout=timeout,
        )
        return FileResponse.model_validate(response.json())


class AsyncFiles:
    """Async resource for the /v1/files endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def upload(
        self,
        *,
        file: FileUpload,
        timeout: float | None = None,
    ) -> FileResponse:
        """Upload a file for use as a listing deliverable (async).

        Returns a file token valid for 24 hours. Pass the token to
        ``listings.set_deliverables()`` or ``orders.deliver()`` to attach it.

        Args:
            file: Tuple of (filename, content_bytes, mime_type).
            timeout: Request timeout override. File uploads may take longer.

        Returns:
            The :class:`~listbee.types.file.FileResponse` with a token ID.
        """
        response = await self._client.post_multipart(
            "/v1/files",
            files={"file": file},
            timeout=timeout,
        )
        return FileResponse.model_validate(response.json())
