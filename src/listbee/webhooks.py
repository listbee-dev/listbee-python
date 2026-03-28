"""Webhook signature verification utilities."""

from __future__ import annotations

import hashlib
import hmac
import time

from listbee._exceptions import WebhookVerificationError


def verify_signature(
    payload: str | bytes,
    header: str,
    secret: str,
    tolerance: int = 300,
) -> None:
    """Verify a ListBee webhook signature.

    Parses the ``X-ListBee-Signature`` header, recomputes the HMAC-SHA256
    signature, and checks the timestamp is within ``tolerance`` seconds.

    Args:
        payload: The raw request body (string or bytes).
        header: The value of the ``X-ListBee-Signature`` header.
        secret: The webhook signing secret (``whsec_...``).
        tolerance: Maximum age in seconds for the timestamp (default 300 = 5 min).

    Raises:
        WebhookVerificationError: If signature is invalid, header is malformed,
            or timestamp exceeds tolerance.
    """
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    parts: dict[str, str] = {}
    for part in header.split(","):
        if "=" in part:
            key, _, value = part.partition("=")
            parts[key.strip()] = value.strip()

    timestamp_str = parts.get("t")
    signature = parts.get("v1")

    if not timestamp_str or not signature:
        raise WebhookVerificationError("Invalid webhook header: missing t or v1 component")

    try:
        timestamp = int(timestamp_str)
    except ValueError:
        raise WebhookVerificationError("Invalid webhook header: non-numeric timestamp")

    now = int(time.time())
    if abs(now - timestamp) > tolerance:
        raise WebhookVerificationError(
            f"Webhook timestamp outside tolerance: {abs(now - timestamp)}s > {tolerance}s"
        )

    signed_content = f"{timestamp_str}.{payload}"
    expected = hmac.new(secret.encode(), signed_content.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise WebhookVerificationError("Webhook signature mismatch")
