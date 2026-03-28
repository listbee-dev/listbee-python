"""Tests for SyncClient auth, config, headers, context manager, and transport errors."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee._exceptions import APIConnectionError, APITimeoutError, ListBeeError


class TestApiKey:
    def test_api_key_from_constructor(self):
        client = SyncClient(api_key="lb_explicit_key")
        assert client._api_key == "lb_explicit_key"

    def test_api_key_from_env_var(self, monkeypatch):
        monkeypatch.setenv("LISTBEE_API_KEY", "lb_env_key_abc123")
        client = SyncClient()
        assert client._api_key == "lb_env_key_abc123"

    def test_constructor_key_takes_precedence_over_env(self, monkeypatch):
        monkeypatch.setenv("LISTBEE_API_KEY", "lb_env_key")
        client = SyncClient(api_key="lb_constructor_key")
        assert client._api_key == "lb_constructor_key"

    def test_missing_api_key_raises_on_build_headers(self, monkeypatch):
        monkeypatch.delenv("LISTBEE_API_KEY", raising=False)
        client = SyncClient()
        with pytest.raises(ListBeeError, match="No API key"):
            client._build_headers()


class TestHeaders:
    def test_bearer_token_in_authorization_header(self, client):
        headers = client._build_headers()
        assert headers["Authorization"] == "Bearer lb_test_key_1234567890abcdef"

    def test_content_type_header(self, client):
        headers = client._build_headers()
        assert headers["Content-Type"] == "application/json"

    def test_user_agent_contains_sdk_name(self, client):
        headers = client._build_headers()
        assert "listbee-python/" in headers["User-Agent"]

    def test_bearer_token_sent_in_request(self, client):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(return_value=httpx.Response(200, json={}))
            client._get("/v1/listings")
        assert route.called
        sent_headers = route.calls[0].request.headers
        assert sent_headers["authorization"] == "Bearer lb_test_key_1234567890abcdef"

    def test_user_agent_sent_in_request(self, client):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(return_value=httpx.Response(200, json={}))
            client._get("/v1/listings")
        assert route.called
        sent_headers = route.calls[0].request.headers
        assert "listbee-python/" in sent_headers["user-agent"]


class TestConfig:
    def test_default_base_url(self):
        client = SyncClient(api_key="lb_key")
        assert client._base_url == "https://api.listbee.so"

    def test_custom_base_url(self):
        client = SyncClient(api_key="lb_key", base_url="https://custom.example.com")
        assert client._base_url == "https://custom.example.com"

    def test_custom_base_url_strips_trailing_slash(self):
        client = SyncClient(api_key="lb_key", base_url="https://custom.example.com/")
        assert client._base_url == "https://custom.example.com"

    def test_default_timeout(self):
        client = SyncClient(api_key="lb_key")
        assert client._timeout == 30.0

    def test_custom_timeout(self):
        client = SyncClient(api_key="lb_key", timeout=60.0)
        assert client._timeout == 60.0

    def test_default_max_retries(self):
        client = SyncClient(api_key="lb_key")
        assert client._max_retries == 3


class TestContextManager:
    def test_sync_context_manager(self):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json={}))
            with SyncClient(api_key="lb_key") as client:
                client._get("/v1/listings")
        # After exiting the context, the internal client should be closed/None
        assert client._http_client is None

    def test_close_sets_http_client_to_none(self, client):
        # Force creation of the internal client
        _ = client._get_http_client()
        assert client._http_client is not None
        client.close()
        assert client._http_client is None


class TestTransportErrors:
    def test_timeout_raises_api_timeout_error(self):
        client = SyncClient(api_key="lb_key", max_retries=0)
        with patch.object(
            client,
            "_get_http_client",
        ) as mock_get:
            mock_client = mock_get.return_value
            mock_client.request.side_effect = httpx.ReadTimeout("timed out")
            with pytest.raises(APITimeoutError, match="timed out"):
                client._get("/v1/listings")

    def test_connect_error_raises_api_connection_error(self):
        client = SyncClient(api_key="lb_key", max_retries=0)
        with patch.object(
            client,
            "_get_http_client",
        ) as mock_get:
            mock_client = mock_get.return_value
            mock_client.request.side_effect = httpx.ConnectError("connection refused")
            with pytest.raises(APIConnectionError, match="connection refused"):
                client._get("/v1/listings")
