import pytest

from listbee.deliverable import Deliverable


class TestDeliverableFile:
    def test_from_path_string(self, tmp_path):
        f = tmp_path / "guide.pdf"
        f.write_bytes(b"fake-pdf")
        d = Deliverable.file(str(f))
        assert d.needs_upload is True
        assert d._filename == "guide.pdf"
        assert d._mime_type == "application/pdf"
        assert d._file_data == b"fake-pdf"

    def test_from_pathlib(self, tmp_path):
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"fake-jpg")
        d = Deliverable.file(f)
        assert d._filename == "photo.jpg"
        assert d._mime_type == "image/jpeg"

    def test_from_bytes(self):
        d = Deliverable.file(b"raw-content", filename="report.pdf")
        assert d._filename == "report.pdf"
        assert d._file_data == b"raw-content"
        assert d._mime_type == "application/pdf"

    def test_from_bytes_requires_filename(self):
        with pytest.raises(ValueError, match="filename"):
            Deliverable.file(b"raw-content")

    def test_from_file_object(self, tmp_path):
        f = tmp_path / "data.zip"
        f.write_bytes(b"zip-data")
        with open(f, "rb") as fh:
            d = Deliverable.file(fh)
        assert d._filename == "data.zip"
        assert d._file_data == b"zip-data"

    def test_override_filename_and_mime(self, tmp_path):
        f = tmp_path / "file.bin"
        f.write_bytes(b"data")
        d = Deliverable.file(str(f), filename="custom.pdf", mime_type="application/pdf")
        assert d._filename == "custom.pdf"
        assert d._mime_type == "application/pdf"

    def test_to_upload_tuple(self):
        d = Deliverable.file(b"content", filename="f.pdf")
        name, data, mime = d.to_upload_tuple()
        assert name == "f.pdf"
        assert data == b"content"
        assert mime == "application/pdf"

    def test_to_api_body_with_token(self):
        d = Deliverable.file(b"x", filename="f.pdf")
        body = d.to_api_body(token="file_tok_123")
        assert body == {"type": "file", "token": "file_tok_123"}


class TestDeliverableFromToken:
    def test_from_token(self):
        d = Deliverable.from_token("file_tok_abc")
        assert d.needs_upload is False
        assert d._token == "file_tok_abc"
        assert d.to_api_body() == {"type": "file", "token": "file_tok_abc"}


class TestDeliverableUrl:
    def test_url(self):
        d = Deliverable.url("https://example.com/secret")
        assert d.needs_upload is False
        assert d.to_api_body() == {"type": "url", "value": "https://example.com/secret"}


class TestDeliverableText:
    def test_text(self):
        d = Deliverable.text("License key: ABCD-1234")
        assert d.needs_upload is False
        assert d.to_api_body() == {"type": "text", "value": "License key: ABCD-1234"}
