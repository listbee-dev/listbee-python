# listbee

[![PyPI](https://img.shields.io/pypi/v/listbee)](https://pypi.org/project/listbee/)
[![Python](https://img.shields.io/pypi/pyversions/listbee)](https://pypi.org/project/listbee/)
[![CI](https://github.com/listbee-dev/listbee-python/actions/workflows/ci.yml/badge.svg)](https://github.com/listbee-dev/listbee-python/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Official Python SDK for the [ListBee API](https://listbee.so) — sell anything, payment collected, digital delivery handled.

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
```

## Resources

| Resource | Methods |
|----------|---------|
| Listings | create, get, list, update, delete, set_deliverables, remove_deliverables, publish |
| Orders | get, list, deliver, refund, ship |
| Customers | get, list |
| Files | upload |
| Webhooks | create, list, update, delete, list_events, retry_event, test |
| Account | get, update, delete |
| Stripe | connect, disconnect |
| Signup | create, verify |
| API Keys | create, list, delete |

```python
from listbee import ListBee

client = ListBee(api_key="lb_...")

# Managed fulfillment — ListBee delivers the file automatically
# 1. Create draft, 2. attach deliverable, 3. publish
listing = client.listings.create(name="SEO Playbook", price=2900)
client.listings.set_deliverables(
    listing.slug,
    deliverables=[{"type": "url", "value": "https://example.com/seo-playbook.pdf"}],
)
listing = client.listings.publish(listing.slug)
print(listing.url)   # https://buy.listbee.so/r7kq2xy9

# External fulfillment — you handle delivery via webhooks
listing = client.listings.create(
    name="Custom T-Shirt",
    price=3500,
    fulfillment="external",
    checkout_schema=[
        {"name": "size", "label": "Size", "type": "select", "options": ["S", "M", "L", "XL"]},
        {"name": "shipping_address", "label": "Shipping Address", "type": "address"},
    ],
)
listing = client.listings.publish(listing.slug)
```

Using an environment variable instead:

```bash
export LISTBEE_API_KEY="lb_..."
```

```python
from listbee import ListBee

client = ListBee()  # reads LISTBEE_API_KEY automatically

listing = client.listings.create(name="SEO Playbook", price=2900)
client.listings.set_deliverables(
    listing.slug,
    deliverables=[{"type": "url", "value": "https://example.com/seo-playbook.pdf"}],
)
listing = client.listings.publish(listing.slug)
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

# Create — managed fulfillment (ListBee delivers the file)
# Listings start as drafts. Attach deliverables then publish.
listing = client.listings.create(
    name="SEO Playbook",
    price=2900,       # $29.00 in cents
)

# Create — external fulfillment (you handle delivery)
listing = client.listings.create(
    name="Custom T-Shirt",
    price=3500,
    fulfillment="external",
    checkout_schema=[
        {"name": "size", "label": "Size", "type": "select", "options": ["S", "M", "L", "XL"]},
        {"name": "color", "label": "Color", "type": "select", "options": ["Black", "White"]},
    ],
)

# Create — all optional params
listing = client.listings.create(
    name="SEO Playbook 2026",
    price=2900,
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
print(listing.id)    # lst_r7kq2xy9m3pR5tW1
# Attach deliverables and publish when ready
client.listings.set_deliverables(
    listing.slug,
    deliverables=[{"type": "url", "value": "https://example.com/seo-playbook.pdf"}],
)
listing = client.listings.publish(listing.slug)
print(listing.url)   # https://buy.listbee.so/m3pr5tw1

# Get by slug
listing = client.listings.get("m3pr5tw1")

# List — auto-paginates
for listing in client.listings.list():
    print(listing.slug, listing.name)

# Update — partial updates
updated = client.listings.update(
    "r7kq2xy9",
    name="SEO Playbook 2026 Updated",
    price=3900,
)

# Update fulfillment mode and checkout schema
updated = client.listings.update(
    "r7kq2xy9",
    fulfillment="external",
    checkout_schema=[
        {"name": "notes", "label": "Special Instructions", "type": "text"},
    ],
)

# Set deliverables on a draft listing (one or more)
client.listings.set_deliverables(
    "r7kq2xy9",
    deliverables=[
        {"type": "url", "value": "https://example.com/seo-playbook.pdf"},
    ],
)

# Remove all deliverables from a draft listing
client.listings.remove_deliverables("r7kq2xy9")

# Publish a draft listing — makes it live and purchasable
listing = client.listings.publish("r7kq2xy9")
print(listing.status)    # "published"

# Delete
client.listings.delete("m3pr5tw1")
```

### Orders

```python
# List all orders
for order in client.orders.list():
    print(order.id, order.status)

# Filter by status
for order in client.orders.list(status="paid"):
    print(order.id, order.buyer_email)

# Get by ID
order = client.orders.get("ord_9xM4kP7nR2qT5wY1")
print(order.listing_id, order.amount)
print(order.checkout_data)        # custom fields from checkout
print(order.shipping_address)     # ShippingAddress or None
print(order.paid_at)              # when payment was confirmed

# Deliver an order — push deliverables for delivery (external fulfillment)
order = client.orders.deliver(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[
        {"type": "text", "value": "Here is your personalized report..."},
    ],
)
print(order.status)               # "fulfilled"

# Deliver with a URL
order = client.orders.deliver(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[
        {"type": "url", "value": "https://example.com/generated-report.pdf"},
    ],
)

# Refund an order — issues a full refund and marks order canceled
order = client.orders.refund("ord_9xM4kP7nR2qT5wY1")
print(order.status)               # "canceled"

# Ship an order — add tracking info
order = client.orders.ship(
    "ord_9xM4kP7nR2qT5wY1",
    carrier="USPS",
    tracking_code="9400111899223456789012",
    seller_note="Ships within 3 business days",
)
print(order.shipped_at)           # datetime when shipped
print(order.carrier)              # "USPS"
```

### Webhooks

```python
from listbee import WebhookEventType

# Create — subscribe to specific events
webhook = client.webhooks.create(
    name="Production endpoint",
    url="https://example.com/webhooks/listbee",
    events=[
        WebhookEventType.ORDER_PAID,
        WebhookEventType.ORDER_FULFILLED,
        WebhookEventType.ORDER_SHIPPED,
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
    events=[WebhookEventType.ORDER_PAID],
)

# Retry a failed webhook event delivery
client.webhooks.retry_event("wh_3mK8nP2qR5tW7xY1", event_id="evt_2nL9oQ3rS6uX8zV2")

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

# Delete account — irreversible
client.account.delete()
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

### Customers

```python
# List all customers (buyers who have placed orders)
for customer in client.customers.list():
    print(customer.email, customer.order_count)

# Get a customer by ID
customer = client.customers.get("acc_4hR9nK2mQ7tV5wX1")
print(customer.email)
print(customer.total_spent)    # total amount in cents
print(customer.order_count)
```

### Files

```python
# Upload a file to use as a deliverable
with open("playbook.pdf", "rb") as f:
    file = client.files.upload(file=f, filename="playbook.pdf")
print(file.id)      # file ID to reference in set_deliverables
print(file.url)     # CDN URL

# Then attach to a listing
client.listings.set_deliverables(
    "r7kq2xy9",
    deliverables=[{"type": "file", "file_id": file.id}],
)
```

### Stripe

```python
# Generate a Stripe Connect onboarding link
connect = client.stripe.connect()
print(connect.url)  # redirect seller here

# Disconnect Stripe
client.stripe.disconnect()
```

## Fulfillment Modes

ListBee supports two fulfillment modes:

**Managed** — ListBee delivers digital content (files, URLs, text) automatically via access grants. Attach deliverables to the listing and ListBee handles the rest.

```python
# Create draft → attach deliverable → publish
listing = client.listings.create(name="SEO Playbook", price=2900)
client.listings.set_deliverables(
    listing.slug,
    deliverables=[{"type": "url", "value": "https://example.com/seo-playbook.pdf"}],
)
listing = client.listings.publish(listing.slug)
```

Upload a file and use it as a deliverable:

```python
with open("playbook.pdf", "rb") as f:
    file = client.files.upload(file=f, filename="playbook.pdf")
client.listings.set_deliverables(
    listing.slug,
    deliverables=[{"type": "file", "file_id": file.id}],
)
```

**External** — ListBee fires `order.paid` webhook, your app handles delivery. Supports physical goods, AI-generated content, services, anything.

```python
listing = client.listings.create(
    name="Custom AI Report",
    price=4900,
    fulfillment="external",
    checkout_schema=[
        {"name": "topic", "label": "Report Topic", "type": "text", "required": True},
    ],
)
listing = client.listings.publish(listing.slug)

# When you receive the order.paid webhook, generate and deliver:
order = client.orders.deliver(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[
        {"type": "text", "value": "Your personalized report..."},
    ],
)
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
listing = client.listings.get("r7kq2xy9")
if not listing.readiness.sellable:
    for action in listing.readiness.actions:
        print(action.code, action.message)
    print(f"Next: {listing.readiness.next}")
```

**Action codes:**

| Code | Meaning |
|------|---------|
| `connect_stripe` | No Stripe account connected — start Connect onboarding |
| `enable_charges` | Stripe charges are disabled — complete Stripe onboarding |
| `update_billing` | ListBee subscription payment failed or unpaid |
| `configure_webhook` | External fulfillment listing needs a webhook endpoint |
| `publish_listing` | Listing is a draft — publish to make it purchasable |
| `webhook_disabled` | Webhook endpoint is disabled |

## Webhook Signature Verification

Verify that incoming webhook requests genuinely come from ListBee before processing them.

```python
from listbee import verify_signature, WebhookVerificationError

# In your webhook handler (e.g. FastAPI, Flask, Django):
payload = request.body      # raw bytes — do not parse first
signature = request.headers["listbee-signature"]
secret = "whsec_..."        # from webhook.secret at creation time

try:
    verify_signature(payload=payload, signature=signature, secret=secret)
except WebhookVerificationError:
    # Signature invalid — reject the request
    return Response(status_code=401)

# Signature valid — safe to process the event
event = json.loads(payload)
```

`verify_signature` raises `WebhookVerificationError` (a subclass of `ListBeeError`) if the signature is missing, malformed, or does not match.

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

    # Create a listing, attach deliverable, publish
    listing = await client.listings.create(name="SEO Playbook", price=2900)
    await client.listings.set_deliverables(
        listing.slug,
        deliverables=[{"type": "url", "value": "https://example.com/seo-playbook.pdf"}],
    )
    listing = await client.listings.publish(listing.slug)
    print(listing.url)

    # Iterate all listings
    async for listing in await client.listings.list():
        print(listing.slug, listing.name)

    # Filter paid orders
    async for order in await client.orders.list(status="paid"):
        print(order.id)

    # Deliver an order (async)
    order = await client.orders.deliver(
        "ord_9xM4kP7nR2qT5wY1",
        deliverables=[{"type": "text", "value": "Generated content here"}],
    )

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
    CustomerResponse,
    FileResponse,
    ListingReadiness,
    AccountReadiness,
    Action,
    ActionResolve,
    Review,
    FaqItem,
    CursorPage,
    CheckoutField,
    ShippingAddress,

    # Models
    DeliverableResponse,  # {object, type, has_content}

    # Enums
    DeliverableType,     # "file" | "url" | "text"
    FulfillmentMode,     # "managed" | "external"
    CheckoutFieldType,   # "text" | "select" | "address" | "date"
    BlurMode,            # "auto" | "true" | "false"
    ListingStatus,       # "draft" | "published"
    OrderStatus,         # "pending" | "paid" | "fulfilled" | "canceled" | "failed"
    WebhookEventType,    # "order.paid" | "order.fulfilled" | "order.shipped" | ...
    ActionCode,          # "connect_stripe" | "configure_webhook" | ...
    ActionKind,          # "api" | "human"

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
from listbee import DeliverableType, FulfillmentMode, ActionCode, ActionKind, WebhookEventType

# Check deliverable type
if listing.has_deliverables and listing.deliverables[0].type == DeliverableType.FILE:
    print("Delivers a file")

# Check fulfillment mode
if listing.fulfillment == FulfillmentMode.EXTERNAL:
    print("External fulfillment — handle delivery yourself")

# Subscribe to specific events
webhook = client.webhooks.create(
    name="Orders only",
    url="https://example.com/hooks",
    events=[
        WebhookEventType.ORDER_PAID,
        WebhookEventType.ORDER_FULFILLED,
        WebhookEventType.ORDER_SHIPPED,
        WebhookEventType.ORDER_REFUNDED,
        WebhookEventType.LISTING_CREATED,
    ],
)

# Branch on action code
for action in listing.readiness.actions:
    if action.code == ActionCode.CONFIGURE_WEBHOOK:
        print(f"Create a webhook: {action.resolve.endpoint}")
    elif action.code == ActionCode.CONNECT_STRIPE:
        print(f"Connect Stripe: {action.resolve.url}")
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
