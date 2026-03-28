"""Tests for webhook signature verification."""

from __future__ import annotations

import hashlib
import hmac
import time

import pytest

from listbee._exceptions import WebhookVerificationError
from listbee.webhooks import verify_signature

SECRET = "whsec_testsecret123"


def _build_sig(body: str, secret: str = SECRET, timestamp: int | None = None) -> str:
    ts = str(timestamp or int(time.time()))
    signed_content = f"{ts}.{body}"
    sig = hmac.new(secret.encode(), signed_content.encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


class TestVerifySignature:
    def test_valid_signature_passes(self):
        body = '{"type":"order.completed"}'
        header = _build_sig(body)
        verify_signature(body, header, SECRET)

    def test_valid_signature_bytes_payload(self):
        body = b'{"type":"order.completed"}'
        header = _build_sig(body.decode())
        verify_signature(body, header, SECRET)

    def test_wrong_secret_raises(self):
        body = '{"type":"order.completed"}'
        header = _build_sig(body, secret="whsec_wrong")
        with pytest.raises(WebhookVerificationError, match="signature"):
            verify_signature(body, header, SECRET)

    def test_expired_timestamp_raises(self):
        body = '{"type":"order.completed"}'
        old_ts = int(time.time()) - 600
        header = _build_sig(body, timestamp=old_ts)
        with pytest.raises(WebhookVerificationError, match="tolerance"):
            verify_signature(body, header, SECRET, tolerance=300)

    def test_custom_tolerance(self):
        body = '{"type":"order.completed"}'
        old_ts = int(time.time()) - 600
        header = _build_sig(body, timestamp=old_ts)
        verify_signature(body, header, SECRET, tolerance=900)

    def test_malformed_header_raises(self):
        with pytest.raises(WebhookVerificationError, match="header"):
            verify_signature('{"ok":true}', "garbage", SECRET)

    def test_missing_v1_raises(self):
        ts = str(int(time.time()))
        with pytest.raises(WebhookVerificationError, match="header"):
            verify_signature('{"ok":true}', f"t={ts}", SECRET)

    def test_missing_timestamp_raises(self):
        with pytest.raises(WebhookVerificationError, match="header"):
            verify_signature('{"ok":true}', "v1=abc123", SECRET)
