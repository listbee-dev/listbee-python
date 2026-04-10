"""Tests for the Store resource."""

from __future__ import annotations

import io
import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee._exceptions import ListBeeError
from listbee.resources.store import Store
from listbee.types.store import StoreReadiness, StoreResponse

STORE_JSON = {
    "object": "store",
    "id": "st_7kQ2xY9mN3pR5tW1vB8a",
    "display_name": "Acme Agency",
    "slug": "acme-agency",
    "bio": "We make great things.",
    "has_avatar": False,
    "url": "https://buy.listbee.so/acme-agency",
    "api_key": None,
    "readiness": {
        "sellable": True,
        "actions": [],
        "next": None,
    },
}

FILE_JSON = {
    "object": "file",
    "id": "file_avatartoken123",
    "filename": "avatar.jpeg",
    "size": 1024,
    "mime_type": "image/jpeg",
    "purpose": "avatar",
    "expires_at": "2026-04-11T15:00:00Z",
    "created_at": "2026-04-10T15:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def store(sync_client):
    return Store(sync_client)


class TestGetStore:
    def test_get_returns_store_response(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.get()
        assert isinstance(result, StoreResponse)
        assert result.id == "st_7kQ2xY9mN3pR5tW1vB8a"
        assert result.display_name == "Acme Agency"
        assert result.slug == "acme-agency"
        assert result.bio == "We make great things."
        assert result.has_avatar is False
        assert result.url == "https://buy.listbee.so/acme-agency"
        assert result.api_key is None

    def test_get_store_readiness_sellable(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.get()
        assert isinstance(result.readiness, StoreReadiness)
        assert result.readiness.sellable is True
        assert result.readiness.actions == []
        assert result.readiness.next is None

    def test_get_store_readiness_not_sellable_with_actions(self, store):
        store_with_actions = {
            **STORE_JSON,
            "readiness": {
                "sellable": False,
                "actions": [
                    {
                        "code": "connect_stripe",
                        "kind": "human",
                        "message": "Connect a Stripe account to accept payments",
                        "resolve": {
                            "method": "GET",
                            "endpoint": None,
                            "url": "https://listbee.so/connect/stripe",
                            "params": None,
                        },
                    }
                ],
                "next": "connect_stripe",
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=store_with_actions))
            result = store.get()
        assert result.readiness.sellable is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "connect_stripe"
        assert result.readiness.next == "connect_stripe"


class TestUpdateStore:
    def test_update_display_name(self, store):
        updated = {**STORE_JSON, "display_name": "New Agency Name"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(display_name="New Agency Name")
        body = json.loads(route.calls[0].request.content)
        assert body["display_name"] == "New Agency Name"
        assert isinstance(result, StoreResponse)
        assert result.display_name == "New Agency Name"

    def test_update_bio(self, store):
        updated = {**STORE_JSON, "bio": "New bio text"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(bio="New bio text")
        body = json.loads(route.calls[0].request.content)
        assert body["bio"] == "New bio text"
        assert result.bio == "New bio text"

    def test_update_slug(self, store):
        updated = {**STORE_JSON, "slug": "new-slug"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(slug="new-slug")
        body = json.loads(route.calls[0].request.content)
        assert body["slug"] == "new-slug"
        assert result.slug == "new-slug"

    def test_update_avatar_with_token(self, store):
        """update(avatar=) passes the file token to the API."""
        updated = {**STORE_JSON, "has_avatar": True}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.update(avatar="file_avatartoken123")
        body = json.loads(route.calls[0].request.content)
        assert body["avatar"] == "file_avatartoken123"
        assert result.has_avatar is True

    def test_update_omits_unset_fields(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            store.update(display_name="Only Name")
        body = json.loads(route.calls[0].request.content)
        assert "bio" not in body
        assert "avatar" not in body
        assert "avatar_url" not in body
        assert "slug" not in body

    def test_update_returns_store_response(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.update()
        assert isinstance(result, StoreResponse)


class TestSetAvatar:
    def test_set_avatar_with_file_token_passes_directly(self, store):
        """file_ token goes straight to update without uploading."""
        updated = {**STORE_JSON, "has_avatar": True}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.set_avatar("file_avatartoken123")
        body = json.loads(route.calls[0].request.content)
        assert body["avatar"] == "file_avatartoken123"
        assert result.has_avatar is True

    def test_set_avatar_with_bytes_uploads_then_updates(self, store):
        """bytes input triggers upload then update."""
        updated = {**STORE_JSON, "has_avatar": True}
        image_bytes = b"\xff\xd8\xff\xe0fake-jpeg"
        with respx.mock(base_url="https://api.listbee.so") as mock:
            upload_route = mock.post("/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
            update_route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.set_avatar(image_bytes)
        # One upload call
        assert upload_route.call_count == 1
        # Update sent with the token
        body = json.loads(update_route.calls[0].request.content)
        assert body["avatar"] == "file_avatartoken123"
        assert result.has_avatar is True

    def test_set_avatar_with_binary_io_uploads_then_updates(self, store):
        """BinaryIO input triggers upload then update."""
        updated = {**STORE_JSON, "has_avatar": True}
        image_bytes = b"\xff\xd8\xff\xe0fake-jpeg"
        buf = io.BytesIO(image_bytes)
        buf.name = "my_avatar.jpg"
        with respx.mock(base_url="https://api.listbee.so") as mock:
            upload_route = mock.post("/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
            update_route = mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))
            result = store.set_avatar(buf)
        assert upload_route.call_count == 1
        body = json.loads(update_route.calls[0].request.content)
        assert body["avatar"] == "file_avatartoken123"
        assert result.has_avatar is True

    def test_set_avatar_with_url_uploads_then_updates(self, store):
        """URL input fetches image, uploads, then updates."""
        updated = {**STORE_JSON, "has_avatar": True}
        image_bytes = b"\xff\xd8\xff\xe0fake-jpeg"

        with respx.mock(base_url="https://api.listbee.so") as api_mock:
            upload_route = api_mock.post("/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
            update_route = api_mock.put("/v1/store").mock(return_value=httpx.Response(200, json=updated))

            with respx.mock() as url_mock:
                url_mock.get("https://example.com/avatar.jpg").mock(
                    return_value=httpx.Response(
                        200,
                        content=image_bytes,
                        headers={"content-type": "image/jpeg"},
                    )
                )
                result = store.set_avatar("https://example.com/avatar.jpg")

        assert upload_route.call_count == 1
        body = json.loads(update_route.calls[0].request.content)
        assert body["avatar"] == "file_avatartoken123"
        assert result.has_avatar is True

    def test_set_avatar_url_non_image_raises(self, store):
        """Non-image content-type from URL raises ListBeeError."""
        with respx.mock() as url_mock:
            url_mock.get("https://example.com/notimage.txt").mock(
                return_value=httpx.Response(
                    200,
                    content=b"hello",
                    headers={"content-type": "text/plain"},
                )
            )
            with pytest.raises(ListBeeError, match="did not return an image"):
                store.set_avatar("https://example.com/notimage.txt")

    def test_set_avatar_url_http_error_raises(self, store):
        """Non-200 response from URL raises ListBeeError."""
        with respx.mock() as url_mock:
            url_mock.get("https://example.com/missing.jpg").mock(return_value=httpx.Response(404, content=b"not found"))
            with pytest.raises(ListBeeError, match="HTTP 404"):
                store.set_avatar("https://example.com/missing.jpg")


class TestStoreHasAvatar:
    def test_has_avatar_true(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json={**STORE_JSON, "has_avatar": True}))
            result = store.get()
        assert result.has_avatar is True

    def test_has_avatar_false_by_default(self, store):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/store").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = store.get()
        assert result.has_avatar is False
