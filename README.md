# listbee

[![PyPI version](https://img.shields.io/pypi/v/listbee?v=1)](https://pypi.org/project/listbee/)
[![CI](https://github.com/listbee-dev/listbee-python/actions/workflows/ci.yml/badge.svg)](https://github.com/listbee-dev/listbee-python/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/listbee?v=1)](https://pypi.org/project/listbee/)

Official Python SDK for the [ListBee API](https://listbee.so) — one API call to sell and deliver digital content.

## Install

```bash
pip install listbee
```

```bash
uv add listbee
```

## Quick Start

```python
from listbee import ListBee

client = ListBee(api_key="lb_...")

listing = client.listings.create(
    name="SEO Playbook",
    price=2900,
    currency="USD",
    content="https://example.com/seo-playbook.pdf",
)
print(listing.url)   # https://buy.listbee.so/seo-playbook
```

Using an environment variable instead:

```bash
export LISTBEE_API_KEY="lb_..."
```

```python
from listbee import ListBee

client = ListBee()  # reads LISTBEE_API_KEY automatically

listing = client.listings.create(
    name="SEO Playbook",
    price=2900,
    currency="USD",
    content="https://example.com/seo-playbook.pdf",
)
print(listing.url)
```

## Authentication

Pass your API key explicitly or via the `LISTBEE_API_KEY` environment variable.

```python
import os
from listbee import ListBee

# Explicit key
client = ListBee(api_key="lb_...")

# Environment variable (LISTBEE_API_KEY)
client = ListBee()

# os.environ lookup
client = ListBee(api_key=os.environ["LISTBEE_API_KEY"])
```

The key is validated lazily — the client constructs successfully even with a missing or invalid key. A `ListBeeError` (specifically `AuthenticationError`) is raised only when you make the first API call.

API keys start with `lb_`. Get yours at [listbee.so](https://listbee.so).

## Resources

### Listings

```python
from listbee import ListBee

client = ListBee(api_key="lb_...")

# Create — minimal
listing = client.listings.create(
    name="SEO Playbook",
    price=2900,       # $29.00 — smallest currency unit
    currency="USD",
    content="https://example.com/seo-playbook.pdf",  # file URL, redirect URL, or plain text
)

# Create — all optional params
listing = client.listings.create(
    name="SEO Playbook 2026",
    price=2900,
    currency="USD",
    content="https://example.com/seo-playbook.pdf",
    description="A comprehensive guide to modern SEO techniques.",
    tagline="Updated for 2026 algorithm changes",
    highlights=["50+ pages", "Actionable tips", "Free updates"],
    cta="Get Instant Access",          # buy button text; defaults to "Buy Now"
    cover_url="https://example.com/cover.png",
    compare_at_price=3900,             # strikethrough price
    badges=["Limited time", "Best seller"],
    cover_blur="auto",                 # "auto" | "true" | "false"
    rating=4.8,
    rating_count=1243,
    reviews=[
        {"name": "Clara D.", "rating": 5.0, "content": "Excellent quality content."}
    ],
    faqs=[
        {"q": "Is this for beginners?", "a": "Yes, completely beginner-friendly."}
    ],
    metadata={"source": "n8n", "campaign": "launch-week"},
)
print(listing.id)    # lst_7kQ2xY9mN3pR5tW1vB8a
print(listing.url)   # https://buy.listbee.so/seo-playbook-2026

# Get by slug
listing = client.listings.get("seo-playbook-2026")

# List — auto-paginates
for listing in client.listings.list():
    print(listing.slug, listing.name)

# Update — partial updates
updated = client.listings.update(
    "seo-playbook",
    name="SEO Playbook 2026 Updated",
    price=3900,
)

# Delete
client.listings.delete("seo-playbook-2026")
```

### Orders

```python
# List all orders
for order in client.orders.list():
    print(order.id, order.status)

# Filter by status
for order in client.orders.list(status="completed"):
    print(order.id, order.email)

# Get by ID
order = client.orders.get("ord_9xM4kP7nR2qT5wY1")
print(order.listing_id, order.amount)
```

### Webhooks

```python
from listbee import WebhookEventType

# Create — subscribe to specific events
webhook = client.webhooks.create(
    name="Production endpoint",
    url="https://example.com/webhooks/listbee",
    events=[
        WebhookEventType.ORDER_COMPLETED,
        WebhookEventType.ORDER_REFUNDED,
    ],
)
print(webhook.id)    # wh_3mK8nP2qR5tW7xY1
print(webhook.secret)

# Create — receive all events (omit events param)
webhook = client.webhooks.create(
    name="Catch-all",
    url="https://example.com/webhooks/listbee-all",
)

# List
webhooks = client.webhooks.list()
for wh in webhooks:
    print(wh.id, wh.name, wh.enabled)

# Update — disable without deleting
webhook = client.webhooks.update("wh_3mK8nP2qR5tW7xY1", enabled=False)

# Update — change URL and events
webhook = client.webhooks.update(
    "wh_3mK8nP2qR5tW7xY1",
    url="https://example.com/webhooks/v2",
    events=[WebhookEventType.ORDER_COMPLETED],
)

# Delete
client.webhooks.delete("wh_3mK8nP2qR5tW7xY1")
```

### Account

```python
account = client.account.get()
print(account.id)           # acc_7kQ2xY9mN3pR5tW1
print(account.email)        # seller@example.com
print(account.plan)         # free | growth | scale
print(account.fee_rate)     # "0.10" (10%)
print(account.readiness.operational)
```

### Signup

Agent self-service onboarding — no API key required:

```python
from listbee import ListBee

client = ListBee(api_key=None)

# Request a signup code
client.signup.create(email="seller@example.com")

# Verify the code — returns account + API key
result = client.signup.verify(email="seller@example.com", code="123456")
print(result.api_key)  # lb_... (one-time display)
```

### API Keys

```python
# List all API keys
for key in client.api_keys.list():
    print(key.id, key.label)

# Create a new key — the key value is only shown once
new_key = client.api_keys.create(label="CI pipeline")
print(new_key.key)  # lb_... (save this immediately)

# Delete a key
client.api_keys.delete("lbk_7kQ2xY9mN3pR5tW1")
```

### Stripe

```python
# Set your Stripe secret key
client.stripe.set_key(key="sk_live_...")

# Generate a Stripe Connect onboarding link
connect = client.stripe.connect()
print(connect.url)  # redirect seller here

# Disconnect Stripe
client.stripe.disconnect()
```

## Readiness System

Every listing and account includes a `readiness` field that tells you whether it can currently accept payments.

- `listing.readiness.sellable` — `True` when buyers can complete a purchase
- `account.readiness.operational` — `True` when the account can sell

When `False`, an `actions` list explains what's needed and how to resolve each item. The `next` field points to the highest-priority action (prefers `kind: api`).

```python
from listbee import ActionKind

account = client.account.get()
if not account.readiness.operational:
    for action in account.readiness.actions:
        if action.kind == ActionKind.API:
            print(f"API action: {action.code} -> {action.resolve.endpoint}")
        else:
            print(f"Manual step: {action.code} -> {action.resolve.url}")
    # Highest priority action
    print(f"Next action: {account.readiness.next}")
```

Listing readiness follows the same shape:

```python
listing = client.listings.get("seo-playbook")
if not listing.readiness.sellable:
    for action in listing.readiness.actions:
        print(action.code, action.message)
    print(f"Next: {listing.readiness.next}")
```

**Action codes:**

| Code | Meaning |
|------|---------|
| `payments_not_configured` | No Stripe account connected |
| `charges_disabled` | Stripe charges are disabled |
| `billing_past_due` | ListBee subscription payment failed |
| `billing_unpaid` | ListBee subscription unpaid |

## Pagination

`listings.list()` and `orders.list()` return a `CursorPage` that auto-fetches subsequent pages when iterated.

```python
# Auto-pagination — iterates all pages transparently
for listing in client.listings.list():
    print(listing.name)

# Manual page control — access current page directly
page = client.listings.list(limit=10)
print(page.data)       # list of ListingResponse on this page
print(page.has_more)   # True if more pages exist
print(page.cursor)     # cursor string for the next page

# Fetch next page manually
if page.has_more:
    next_page = client.listings.list(limit=10, cursor=page.cursor)
    print(next_page.data)
```

## Error Handling

```
ListBeeError
├── APIConnectionError   # network error — request never reached the server
├── APITimeoutError      # request timed out
└── APIStatusError       # server returned 4xx/5xx
    ├── AuthenticationError    # 401 — invalid or missing API key
    ├── NotFoundError          # 404 — resource not found
    ├── ConflictError          # 409 — resource conflict
    ├── ValidationError        # 422 — request validation failed
    ├── RateLimitError         # 429 — rate limit exceeded
    └── InternalServerError    # 500+ — server-side error
```

Catch specific errors:

```python
from listbee import (
    ListBee,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

client = ListBee(api_key="lb_...")

try:
    listing = client.listings.get("does-not-exist")
except NotFoundError as e:
    print(e.status)   # 404
    print(e.code)     # machine-readable code
    print(e.detail)   # human-readable explanation
    print(e.title)    # short stable label
    print(e.type)     # URI pointing to docs
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Resets at {e.reset}, {e.remaining}/{e.limit} remaining")
except ValidationError as e:
    print(f"Bad request — field: {e.param}, detail: {e.detail}")
except APIConnectionError:
    print("Network error — check your connection")
except APITimeoutError:
    print("Request timed out")
except APIStatusError as e:
    # Catch-all for unexpected status codes
    print(f"API error {e.status}: {e.detail}")
```

Error responses follow [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) (Problem Details). All `APIStatusError` subclasses expose:

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `int` | HTTP status code |
| `code` | `str` | Machine-readable error code |
| `detail` | `str` | Specific explanation |
| `title` | `str` | Short, stable error category label |
| `type` | `str` | URI identifying the error type |
| `param` | `str \| None` | Request field that caused the error |

`RateLimitError` additionally exposes `limit`, `remaining`, and `reset` (parsed from response headers).

## Async Usage

Use `AsyncListBee` for async frameworks (FastAPI, aiohttp, etc.):

```python
import asyncio
from listbee import AsyncListBee

async def main():
    client = AsyncListBee(api_key="lb_...")

    # Create a listing
    listing = await client.listings.create(
        name="SEO Playbook",
        price=2900,
        currency="USD",
        content="https://example.com/seo-playbook.pdf",
    )
    print(listing.url)

    # Iterate all listings
    async for listing in await client.listings.list():
        print(listing.slug, listing.name)

    # Filter completed orders
    async for order in await client.orders.list(status="completed"):
        print(order.id)

asyncio.run(main())
```

Use as an async context manager to ensure the connection is closed:

```python
async def main():
    async with AsyncListBee(api_key="lb_...") as client:
        account = await client.account.get()
        print(account.email)
```

The sync client also supports context manager usage:

```python
with ListBee(api_key="lb_...") as client:
    for listing in client.listings.list():
        print(listing.name)
```

## Configuration

```python
from listbee import ListBee

client = ListBee(
    api_key="lb_...",
    timeout=60.0,           # default: 30.0 seconds
    max_retries=5,          # default: 3; retries on 429/500/502/503/504
    base_url="https://api.listbee.so",  # default; override for testing
)
```

**Note:** `listings.create()` uses a separate default timeout of **120 seconds** because cover image processing can take longer. Pass `timeout=` explicitly to override it:

```python
listing = client.listings.create(
    name="Quick listing",
    price=999,
    currency="USD",
    content="https://example.com/file.pdf",
    timeout=30.0,  # override the 120s default for this call
)
```

## Types and Enums

All types are importable directly from `listbee`:

```python
from listbee import (
    # Clients
    ListBee,
    AsyncListBee,

    # Response models
    ListingResponse,
    OrderResponse,
    WebhookResponse,
    AccountResponse,
    ListingReadiness,
    AccountReadiness,
    Action,
    ActionResolve,
    Review,
    FaqItem,
    CursorPage,

    # Enums
    ContentType,        # "file" | "url" | "text"
    BlurMode,           # "auto" | "true" | "false"
    ListingStatus,      # "published"
    OrderStatus,        # "completed"
    WebhookEventType,   # "order.completed" | "order.refunded" | ...
    ActionCode,         # "payments_not_configured" | ...
    ActionKind,         # "api" | "human"

    # Exceptions
    ListBeeError,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    ConflictError,
    ValidationError,
    RateLimitError,
    InternalServerError,
)
```

Use enums to avoid magic strings:

```python
from listbee import ContentType, ActionCode, ActionKind, WebhookEventType

# Check content type
if listing.content_type == ContentType.FILE:
    print("Delivers a file")

# Subscribe to specific events
webhook = client.webhooks.create(
    name="Orders only",
    url="https://example.com/hooks",
    events=[
        WebhookEventType.ORDER_COMPLETED,
        WebhookEventType.ORDER_REFUNDED,
        WebhookEventType.ORDER_DISPUTED,
        WebhookEventType.ORDER_DISPUTE_CLOSED,
        WebhookEventType.LISTING_CREATED,
    ],
)

# Branch on action code
for action in listing.readiness.actions:
    if action.code == ActionCode.PAYMENTS_NOT_CONFIGURED:
        print(f"Connect Stripe: {action.resolve.url}")
    elif action.code == ActionCode.CHARGES_DISABLED:
        print(f"Enable charges: {action.resolve.url}")
```

## Requirements

- Python >= 3.10

## License

Apache-2.0. See [LICENSE](LICENSE).

## Links

- [Documentation](https://docs.listbee.so)
- [API Reference](https://docs.listbee.so/api)
- [GitHub](https://github.com/listbee-dev/listbee-python)
- [PyPI](https://pypi.org/project/listbee/)
- [Changelog](CHANGELOG.md)
