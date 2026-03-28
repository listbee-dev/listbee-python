"""Tests for retry behavior: status codes, backoff, exhaustion."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee._exceptions import (
    AuthenticationError,
    InternalServerError,
    ValidationError,
)

ERROR_BODY = {
    "type": "https://docs.listbee.so/errors/server-error",
    "title": "Internal Server Error",
    "status": 500,
    "detail": "Something went wrong",
    "code": "internal_error",
}

AUTH_ERROR_BODY = {
    "type": "https://docs.listbee.so/errors/authentication",
    "title": "Unauthorized",
    "status": 401,
    "detail": "Invalid API key",
    "code": "invalid_api_key",
}

VALIDATION_ERROR_BODY = {
    "type": "https://docs.listbee.so/errors/validation",
    "title": "Unprocessable Entity",
    "status": 422,
    "detail": "Invalid input",
    "code": "invalid_input",
}

SUCCESS_BODY = {"id": "lst_abc", "object": "listing"}


def test_500_then_200_retries_and_succeeds():
    """A 500 followed by a 200 should succeed after one retry."""
    client = SyncClient(api_key="lb_key", max_retries=1)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug")
        route.side_effect = [
            httpx.Response(500, json=ERROR_BODY),
            httpx.Response(200, json=SUCCESS_BODY),
        ]
        with patch("time.sleep"):
            response = client._get("/v1/listings/my-slug")

    assert response.status_code == 200
    assert route.call_count == 2


def test_429_then_200_retries_and_succeeds():
    """A 429 followed by a 200 should succeed after one retry."""
    client = SyncClient(api_key="lb_key", max_retries=1)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug")
        route.side_effect = [
            httpx.Response(429, json={**ERROR_BODY, "status": 429, "title": "Too Many Requests"}),
            httpx.Response(200, json=SUCCESS_BODY),
        ]
        with patch("time.sleep"):
            response = client._get("/v1/listings/my-slug")

    assert response.status_code == 200
    assert route.call_count == 2


def test_422_no_retry_raises_validation_error():
    """A 422 should not be retried and must raise ValidationError."""
    client = SyncClient(api_key="lb_key", max_retries=1)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug").mock(return_value=httpx.Response(422, json=VALIDATION_ERROR_BODY))
        with pytest.raises(ValidationError):
            client._get("/v1/listings/my-slug")

    assert route.call_count == 1


def test_401_no_retry_raises_authentication_error():
    """A 401 should not be retried and must raise AuthenticationError."""
    client = SyncClient(api_key="lb_key", max_retries=1)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug").mock(return_value=httpx.Response(401, json=AUTH_ERROR_BODY))
        with pytest.raises(AuthenticationError):
            client._get("/v1/listings/my-slug")

    assert route.call_count == 1


def test_500_all_attempts_raises_internal_server_error():
    """When all retry attempts return 500, InternalServerError should be raised."""
    client = SyncClient(api_key="lb_key", max_retries=1)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug")
        route.side_effect = [
            httpx.Response(500, json=ERROR_BODY),
            httpx.Response(500, json=ERROR_BODY),
        ]
        with patch("time.sleep"), pytest.raises(InternalServerError):
            client._get("/v1/listings/my-slug")

    assert route.call_count == 2


def test_retry_after_header_is_respected():
    """Retry-After header should override the exponential backoff delay."""
    client = SyncClient(api_key="lb_key", max_retries=1)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug")
        route.side_effect = [
            httpx.Response(429, json=ERROR_BODY, headers={"retry-after": "5"}),
            httpx.Response(200, json=SUCCESS_BODY),
        ]
        with patch("listbee._base_client.time") as mock_time:
            client._get("/v1/listings/my-slug")

    mock_time.sleep.assert_called_once_with(5.0)
    assert route.call_count == 2


def test_max_retries_zero_never_retries():
    """With max_retries=0, a 500 must raise immediately without retrying."""
    client = SyncClient(api_key="lb_key", max_retries=0)
    with respx.mock(base_url="https://api.listbee.so") as mock:
        route = mock.get("/v1/listings/my-slug").mock(return_value=httpx.Response(500, json=ERROR_BODY))
        with pytest.raises(InternalServerError):
            client._get("/v1/listings/my-slug")

    assert route.call_count == 1
