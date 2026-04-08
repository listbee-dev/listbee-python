"""Raw response wrapper — access headers, status code, and request ID alongside parsed data."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class RawResponse(Generic[T]):
    """Wraps a raw httpx.Response and provides typed parsing.

    Usage:
        raw = client.account.with_raw_response.get()
        print(raw.request_id)   # x-request-id header
        print(raw.status_code)  # 200
        account = raw.parse()   # AccountResponse
    """

    def __init__(self, response: Any, model: type[T]) -> None:
        self._response = response
        self._model = model

    @property
    def headers(self) -> dict[str, str]:
        """All response headers as a plain dict."""
        return dict(self._response.headers)

    @property
    def status_code(self) -> int:
        """HTTP status code."""
        return self._response.status_code

    @property
    def request_id(self) -> str | None:
        """Value of the ``x-request-id`` response header, if present."""
        return self._response.headers.get("x-request-id")

    def parse(self) -> T:
        """Parse and return the response body as the expected model."""
        return self._model.model_validate(self._response.json())
