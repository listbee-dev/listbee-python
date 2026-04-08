"""Standalone helper utilities for the ListBee Python SDK."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from listbee._client import AsyncListBee, ListBee
    from listbee.types.shared import Action

from listbee.types.shared import WebhookEventType
from listbee.webhooks import verify_signature

# ---------------------------------------------------------------------------
# Currency helpers
# ---------------------------------------------------------------------------

ZERO_DECIMAL_CURRENCIES = frozenset(
    {
        "bif",
        "clp",
        "djf",
        "gnf",
        "jpy",
        "kmf",
        "krw",
        "mga",
        "pyg",
        "rwf",
        "ugx",
        "vnd",
        "vuv",
        "xaf",
        "xof",
        "xpf",
    }
)

CURRENCY_SYMBOLS: dict[str, str] = {
    "usd": "$",
    "eur": "\u20ac",
    "gbp": "\u00a3",
    "jpy": "\u00a5",
    "cad": "CA$",
    "aud": "A$",
    "chf": "CHF\u00a0",
    "sgd": "S$",
    "hkd": "HK$",
    "nzd": "NZ$",
    "sek": "kr\u00a0",
    "nok": "kr\u00a0",
    "dkk": "kr\u00a0",
    "krw": "\u20a9",
    "brl": "R$",
    "mxn": "MX$",
    "inr": "\u20b9",
    "pln": "z\u0142",
    "zar": "R",
    "myr": "RM",
    "thb": "\u0e3f",
    "php": "\u20b1",
    "ils": "\u20aa",
    "aed": "AED\u00a0",
    "idr": "Rp",
    "cop": "COL$",
    "ars": "AR$",
}


def format_price(amount_minor: int, currency: str) -> str:
    """Format a minor-unit amount as a human-readable price string.

    Args:
        amount_minor: Amount in the smallest currency unit (e.g. 2900 cents = $29.00).
        currency: Three-letter ISO 4217 currency code (case-insensitive).

    Returns:
        Formatted price string with currency symbol (e.g. ``"$29.00"`` or ``"¥1,500"``).

    Examples:
        >>> format_price(2900, "USD")
        '$29.00'
        >>> format_price(1500, "JPY")
        '¥1,500'
        >>> format_price(1999, "EUR")
        '€19.99'
    """
    cur = currency.lower()
    symbol = CURRENCY_SYMBOLS.get(cur, f"{currency.upper()}\u00a0")
    if cur in ZERO_DECIMAL_CURRENCIES:
        return f"{symbol}{amount_minor:,}"
    major = amount_minor / 100
    return f"{symbol}{major:,.2f}"


def to_minor(amount_major: float, currency: str) -> int:
    """Convert a major-unit amount to the smallest currency unit.

    Args:
        amount_major: Amount in major currency units (e.g. 29.00 dollars).
        currency: Three-letter ISO 4217 currency code (case-insensitive).

    Returns:
        Amount in the smallest currency unit as an integer (e.g. 2900 cents).

    Examples:
        >>> to_minor(29.00, "USD")
        2900
        >>> to_minor(1500, "JPY")
        1500
    """
    if currency.lower() in ZERO_DECIMAL_CURRENCIES:
        return int(amount_major)
    return round(amount_major * 100)


def from_minor(amount_minor: int, currency: str) -> float:
    """Convert a minor-unit amount to major currency units.

    Args:
        amount_minor: Amount in the smallest currency unit (e.g. 2900 cents).
        currency: Three-letter ISO 4217 currency code (case-insensitive).

    Returns:
        Amount in major currency units (e.g. 29.0 dollars).

    Examples:
        >>> from_minor(2900, "USD")
        29.0
        >>> from_minor(1500, "JPY")
        1500.0
    """
    if currency.lower() in ZERO_DECIMAL_CURRENCIES:
        return float(amount_minor)
    return amount_minor / 100


# ---------------------------------------------------------------------------
# Action resolution helpers
# ---------------------------------------------------------------------------


def resolve_action(client: ListBee, action: Action) -> Any:
    """Execute an API action returned by the readiness system.

    Dispatches the appropriate HTTP method based on ``action.resolve.method``
    and returns the parsed JSON response body.

    Args:
        client: Synchronous :class:`~listbee.ListBee` client instance.
        action: An :class:`~listbee.types.shared.Action` from a readiness response.

    Returns:
        Parsed JSON response as a dict, or ``None`` for DELETE requests.

    Raises:
        ValueError: If the action requires human intervention (no API endpoint).

    Examples:
        >>> listing = client.listings.get("my-listing")
        >>> action = listing.readiness.next_action
        >>> if action and action.kind == "api":
        ...     resolve_action(client, action)
    """
    resolve = action.resolve
    if resolve.endpoint is None:
        raise ValueError(f"Action '{action.code}' requires human intervention (no API endpoint)")
    method = resolve.method.upper()
    if method == "POST":
        resp = client.post(resolve.endpoint, json=resolve.params or {})
    elif method == "PUT":
        resp = client.put(resolve.endpoint, json=resolve.params or {})
    elif method == "DELETE":
        client.delete(resolve.endpoint)
        return None
    else:
        resp = client.get(resolve.endpoint)
    return resp.json()


async def resolve_action_async(client: AsyncListBee, action: Action) -> Any:
    """Execute an API action returned by the readiness system (async).

    Async variant of :func:`resolve_action`.

    Args:
        client: Asynchronous :class:`~listbee.AsyncListBee` client instance.
        action: An :class:`~listbee.types.shared.Action` from a readiness response.

    Returns:
        Parsed JSON response as a dict, or ``None`` for DELETE requests.

    Raises:
        ValueError: If the action requires human intervention (no API endpoint).
    """
    resolve = action.resolve
    if resolve.endpoint is None:
        raise ValueError(f"Action '{action.code}' requires human intervention (no API endpoint)")
    method = resolve.method.upper()
    if method == "POST":
        resp = await client.post(resolve.endpoint, json=resolve.params or {})
    elif method == "PUT":
        resp = await client.put(resolve.endpoint, json=resolve.params or {})
    elif method == "DELETE":
        await client.delete(resolve.endpoint)
        return None
    else:
        resp = await client.get(resolve.endpoint)
    return resp.json()


# ---------------------------------------------------------------------------
# Webhook parsing
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedWebhookEvent:
    """A verified and parsed webhook event.

    Attributes:
        type: The event type as a :class:`~listbee.types.shared.WebhookEventType` enum value.
        data: The raw event data payload as a dictionary.
    """

    type: WebhookEventType
    data: dict[str, Any]


def parse_webhook_event(
    payload: str | bytes,
    header: str,
    secret: str,
    *,
    tolerance: int = 300,
) -> ParsedWebhookEvent:
    """Verify and parse a ListBee webhook event.

    Verifies the ``X-ListBee-Signature`` header, then deserializes the payload
    into a :class:`ParsedWebhookEvent`.

    Args:
        payload: The raw request body (string or bytes).
        header: The value of the ``X-ListBee-Signature`` header.
        secret: The webhook signing secret (``whsec_...``).
        tolerance: Maximum age in seconds for the timestamp (default 300 = 5 min).

    Returns:
        A :class:`ParsedWebhookEvent` with ``type`` and ``data`` attributes.

    Raises:
        :class:`~listbee.WebhookVerificationError`: If the signature is invalid,
            the header is malformed, or the timestamp exceeds tolerance.

    Examples:
        >>> event = parse_webhook_event(request.body, request.headers["X-ListBee-Signature"], secret)
        >>> if event.type == WebhookEventType.ORDER_PAID:
        ...     fulfill_order(event.data["id"])
    """
    verify_signature(payload, header, secret, tolerance=tolerance)
    body = _json.loads(payload)
    return ParsedWebhookEvent(
        type=WebhookEventType(body["event_type"]),
        data=body["data"],
    )
