"""Tests for the files resource."""

import httpx
import respx

from listbee._base_client import SyncClient
from listbee.resources.files import Files
from listbee.types.file import FileResponse

FILE_JSON = {
    "object": "file",
    "id": "file_7kQ2xY9mN3pR5tW1vB8a01",
    "filename": "ebook.pdf",
    "size": 2458631,
    "mime_type": "application/pdf",
    "purpose": "deliverable",
    "expires_at": "2026-04-04T15:00:00Z",
    "created_at": "2026-04-03T15:00:00Z",
}


class TestUploadFile:
    def test_upload_returns_file_response(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        files = Files(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
            result = files.upload(file=("ebook.pdf", b"fake-pdf-content", "application/pdf"))
        assert isinstance(result, FileResponse)
        assert result.id == "file_7kQ2xY9mN3pR5tW1vB8a01"
        assert result.filename == "ebook.pdf"
        assert result.size == 2458631

    def test_upload_sends_multipart_request(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        files = Files(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
            files.upload(file=("ebook.pdf", b"fake-pdf-content", "application/pdf"))
        sent_headers = route.calls[0].request.headers
        assert "multipart/form-data" in sent_headers.get("content-type", "")

    def test_upload_default_purpose_is_deliverable(self):
        """Default purpose is deliverable — field present in request body."""
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        files = Files(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
            files.upload(file=("ebook.pdf", b"fake-pdf-content", "application/pdf"))
        # The purpose field should be present in the multipart body
        body_text = route.calls[0].request.content.decode(errors="replace")
        assert "deliverable" in body_text

    def test_upload_cover_purpose(self):
        """purpose='cover' is sent in the multipart request."""
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        files = Files(client)
        cover_json = {**FILE_JSON, "purpose": "cover", "filename": "cover.jpg", "mime_type": "image/jpeg"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/files").mock(return_value=httpx.Response(201, json=cover_json))
            result = files.upload(
                file=("cover.jpg", b"fake-image-content", "image/jpeg"),
                purpose="cover",
            )
        body_text = route.calls[0].request.content.decode(errors="replace")
        assert "cover" in body_text
        assert result.purpose == "cover"

    def test_upload_avatar_purpose(self):
        """purpose='avatar' is sent in the multipart request."""
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        files = Files(client)
        avatar_json = {**FILE_JSON, "purpose": "avatar", "filename": "avatar.png", "mime_type": "image/png"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/files").mock(return_value=httpx.Response(201, json=avatar_json))
            result = files.upload(
                file=("avatar.png", b"fake-image-content", "image/png"),
                purpose="avatar",
            )
        body_text = route.calls[0].request.content.decode(errors="replace")
        assert "avatar" in body_text
        assert result.purpose == "avatar"
