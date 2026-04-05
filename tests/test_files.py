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
