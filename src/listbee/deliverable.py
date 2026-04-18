"""Deliverable input builder — type-safe, developer-friendly file handling."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import IO

FileSource = str | os.PathLike[str] | IO[bytes] | bytes


class Deliverable:
    """Input builder for deliverables. Use factory methods — do not instantiate directly.

    Examples::

        Deliverable.file("assets/sunset.jpg")
        Deliverable.file(pdf_bytes, filename="report.pdf")
        Deliverable.from_token("file_tok_abc")
        Deliverable.url("https://example.com/secret")
        Deliverable.text("License key: ABCD-1234")
    """

    __slots__ = ("_type", "_file_data", "_filename", "_mime_type", "_value", "_token")

    @classmethod
    def file(
        cls,
        source: FileSource,
        *,
        filename: str | None = None,
        mime_type: str | None = None,
    ) -> Deliverable:
        """Create a file deliverable from a path, file object, or bytes.

        Args:
            source: File path (str/Path), open file object, or raw bytes.
            filename: Override filename. Auto-detected from path/file object.
            mime_type: Override MIME type. Auto-detected from filename.
        """
        inst = object.__new__(cls)
        inst._type = "file"
        inst._token = None
        inst._value = None

        if isinstance(source, str | os.PathLike):
            path = Path(source).expanduser()
            inst._filename = filename or path.name
            inst._mime_type = mime_type or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            inst._file_data = path.read_bytes()
        elif isinstance(source, bytes):
            if not filename:
                raise ValueError("filename is required when source is bytes")
            inst._filename = filename
            inst._mime_type = mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            inst._file_data = source
        elif hasattr(source, "read"):
            inst._file_data = source.read()
            name = getattr(source, "name", None)
            inst._filename = filename or (os.path.basename(name) if name else "upload")
            inst._mime_type = mime_type or mimetypes.guess_type(inst._filename)[0] or "application/octet-stream"
        else:
            raise TypeError(f"Unsupported file source type: {type(source)}")
        return inst

    @classmethod
    def from_token(cls, token: str) -> Deliverable:
        """Create a file deliverable from a pre-uploaded file token.

        Args:
            token: File token from ``client.files.upload()`` (valid 24 hours).
        """
        inst = object.__new__(cls)
        inst._type = "file"
        inst._token = token
        inst._value = None
        inst._file_data = None
        inst._filename = None
        inst._mime_type = None
        return inst

    @classmethod
    def url(cls, url: str) -> Deliverable:
        """Create a URL redirect deliverable.

        Args:
            url: HTTPS URL buyers will be redirected to after purchase.
        """
        inst = object.__new__(cls)
        inst._type = "url"
        inst._value = url
        inst._token = None
        inst._file_data = None
        inst._filename = None
        inst._mime_type = None
        return inst

    @classmethod
    def text(cls, content: str) -> Deliverable:
        """Create a plain text deliverable.

        Args:
            content: Text content delivered to the buyer (e.g., license key, instructions).
        """
        inst = object.__new__(cls)
        inst._type = "text"
        inst._value = content
        inst._token = None
        inst._file_data = None
        inst._filename = None
        inst._mime_type = None
        return inst

    @property
    def needs_upload(self) -> bool:
        """True if this deliverable has file data that must be uploaded first."""
        return self._type == "file" and self._file_data is not None

    def to_upload_tuple(self) -> tuple[str, bytes, str]:
        """SDK internal — returns (filename, bytes, mime_type) for files.upload()."""
        return (self._filename, self._file_data, self._mime_type)

    def to_api_body(self, token: str | None = None) -> dict[str, str | None]:
        """SDK internal — returns JSON body for deliverable field on listing create/update."""
        if self._type == "file":
            return {"type": "file", "token": token or self._token}
        return {"type": self._type, "content": self._value}

    def __repr__(self) -> str:
        if self._type == "file" and self._file_data is not None:
            return f"Deliverable.file({self._filename!r})"
        if self._type == "file" and self._token:
            return f"Deliverable.from_token({self._token!r})"
        if self._type == "url":
            return f"Deliverable.url({self._value!r})"
        return f"Deliverable.text({self._value!r})"
