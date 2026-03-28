"""Base HTTP clients (sync and async) for the ListBee SDK."""

from __future__ import annotations

import asyncio
import os
import random
import time
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from listbee._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
    RETRY_STATUS_CODES,
)
from listbee._exceptions import (
    APIConnectionError,
    APITimeoutError,
    ListBeeError,
    raise_for_status,
)
from listbee._pagination import AsyncCursorPage, SyncCursorPage

try:
    from importlib.metadata import version

    _SDK_VERSION = version("listbee")
except Exception:
    _SDK_VERSION = "0.0.0"

T = TypeVar("T", bound=BaseModel)


class BaseClient:
    """Shared configuration and logic for sync and async clients."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._api_key = api_key or os.environ.get("LISTBEE_API_KEY")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    @property
    def base_url(self) -> str:
        """The base URL this client sends requests to."""
        return self._base_url

    def _ensure_api_key(self) -> str:
        if not self._api_key:
            raise ListBeeError("No API key provided. Set api_key= or the LISTBEE_API_KEY environment variable.")
        return self._api_key

    def _build_headers(self) -> dict[str, str]:
        api_key = self._ensure_api_key()
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"listbee-python/{_SDK_VERSION}",
        }

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Return True if the request should be retried."""
        return status_code in RETRY_STATUS_CODES and attempt < self._max_retries

    def _retry_delay(self, attempt: int, headers: httpx.Headers) -> float:
        """Return seconds to wait before the next retry attempt.

        Respects the Retry-After response header when present.
        Falls back to exponential backoff with jitter.
        """
        retry_after = headers.get("retry-after")
        if retry_after is not None:
            try:
                delay = float(retry_after)
                return min(delay, MAX_RETRY_DELAY)
            except ValueError:
                pass

        # Exponential backoff: 0.5s, 1s, 2s, … capped at 30s, plus jitter
        delay = INITIAL_RETRY_DELAY * (2**attempt)
        delay = min(delay, MAX_RETRY_DELAY)
        # Add ±25% jitter
        jitter = delay * 0.25 * (random.random() * 2 - 1)
        return max(0.0, delay + jitter)


class SyncClient(BaseClient):
    """Synchronous HTTP client backed by httpx."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http_client: httpx.Client | None = None

    def _get_http_client(self) -> httpx.Client:
        if self._http_client is None:
            self._http_client = httpx.Client(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._http_client

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self) -> SyncClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        headers = self._build_headers()
        effective_timeout = timeout if timeout is not None else self._timeout
        client = self._get_http_client()

        attempt = 0
        last_response: httpx.Response | None = None

        while True:
            try:
                response = client.request(
                    method,
                    path,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=effective_timeout,
                )
            except httpx.TimeoutException as exc:
                raise APITimeoutError(f"Request timed out: {exc}") from exc
            except httpx.ConnectError as exc:
                raise APIConnectionError(f"Connection error: {exc}") from exc

            if response.is_error:
                last_response = response
                if self._should_retry(response.status_code, attempt):
                    delay = self._retry_delay(attempt, response.headers)
                    time.sleep(delay)
                    attempt += 1
                    continue

                # Non-retryable error: parse and raise
                try:
                    body = response.json()
                except Exception:
                    body = {}
                raise_for_status(response.status_code, body, dict(response.headers))

            return response

        # Exhausted retries — raise from last response
        # (unreachable in normal flow; kept for type completeness)
        assert last_response is not None  # pragma: no cover
        try:
            body = last_response.json()
        except Exception:
            body = {}
        raise_for_status(last_response.status_code, body, dict(last_response.headers))  # pragma: no cover

    def _get(self, path: str, *, params: dict[str, Any] | None = None, timeout: float | None = None) -> httpx.Response:
        return self._request("GET", path, params=params, timeout=timeout)

    def _post(self, path: str, *, json: Any = None, timeout: float | None = None) -> httpx.Response:
        return self._request("POST", path, json=json, timeout=timeout)

    def _put(self, path: str, *, json: Any = None, timeout: float | None = None) -> httpx.Response:
        return self._request("PUT", path, json=json, timeout=timeout)

    def _delete(self, path: str, *, timeout: float | None = None) -> httpx.Response:
        return self._request("DELETE", path, timeout=timeout)

    def _get_page(self, path: str, params: dict[str, Any], model: type[T]) -> SyncCursorPage[T]:
        """Fetch a paginated list response and return a SyncCursorPage."""
        response = self._get(path, params=params)
        body = response.json()
        items = [model.model_validate(item) for item in body.get("data", [])]
        return SyncCursorPage(
            data=items,
            has_more=body.get("has_more", False),
            cursor=body.get("cursor"),
            client=self,
            path=path,
            params=params,
            model=model,
        )


class AsyncClient(BaseClient):
    """Asynchronous HTTP client backed by httpx.AsyncClient."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http_client: httpx.AsyncClient | None = None

    def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._http_client

    async def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        headers = self._build_headers()
        effective_timeout = timeout if timeout is not None else self._timeout
        client = self._get_http_client()

        attempt = 0
        last_response: httpx.Response | None = None

        while True:
            try:
                response = await client.request(
                    method,
                    path,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=effective_timeout,
                )
            except httpx.TimeoutException as exc:
                raise APITimeoutError(f"Request timed out: {exc}") from exc
            except httpx.ConnectError as exc:
                raise APIConnectionError(f"Connection error: {exc}") from exc

            if response.is_error:
                last_response = response
                if self._should_retry(response.status_code, attempt):
                    delay = self._retry_delay(attempt, response.headers)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue

                try:
                    body = response.json()
                except Exception:
                    body = {}
                raise_for_status(response.status_code, body, dict(response.headers))

            return response

        # Exhausted retries — raise from last response
        assert last_response is not None  # pragma: no cover
        try:
            body = last_response.json()
        except Exception:
            body = {}
        raise_for_status(last_response.status_code, body, dict(last_response.headers))  # pragma: no cover

    async def _get(
        self, path: str, *, params: dict[str, Any] | None = None, timeout: float | None = None
    ) -> httpx.Response:
        return await self._request("GET", path, params=params, timeout=timeout)

    async def _post(self, path: str, *, json: Any = None, timeout: float | None = None) -> httpx.Response:
        return await self._request("POST", path, json=json, timeout=timeout)

    async def _put(self, path: str, *, json: Any = None, timeout: float | None = None) -> httpx.Response:
        return await self._request("PUT", path, json=json, timeout=timeout)

    async def _delete(self, path: str, *, timeout: float | None = None) -> httpx.Response:
        return await self._request("DELETE", path, timeout=timeout)

    async def _get_page(self, path: str, params: dict[str, Any], model: type[T]) -> AsyncCursorPage[T]:
        """Fetch a paginated list response and return an AsyncCursorPage."""
        response = await self._get(path, params=params)
        body = response.json()
        items = [model.model_validate(item) for item in body.get("data", [])]
        return AsyncCursorPage(
            data=items,
            has_more=body.get("has_more", False),
            cursor=body.get("cursor"),
            client=self,
            path=path,
            params=params,
            model=model,
        )
