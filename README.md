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
from listbee import ListBee, CheckoutField

client = ListBee(api_key="lb_...")
```

## Resources

| Resource | Methods |
|----------|---------|
| Bootstrap | start, verify, create_store |
| Store | get, update |
| Listings | create, get, list, update, delete, set_deliverables, remove_deliverables, add_deliverable, remove_deliverable, create_complete, publish |
| Orders | get, list, fulfill, refund |
| Customers | get, list |
| Files | upload |
| Webhooks | create, list, update, delete, list_events, retry_event, test |
| Account | get, update, delete |
| Stripe | connect, disconnect |
| Utility | ping, plans |

```python
from listbee import ListBee, Deliverable

client = ListBee(api_key="lb_...")

# Static content — ListBee delivers pre-attached file automatically
# One-shot: create listing + attach deliverable + publish
listing = client.listings.create_complete(
    name="SEO Playbook",
    price=2900,
    deliverables=[Deliverable.url("https://example.com/seo-playbook.pdf")],
)
listing = client.listings.publish(listing.id)
print(listing.url)   # https://buy.listbee.so/r7kq2xy9

# External fulfillment — set a URL and you handle delivery
from listbee import CheckoutField

listing = client.listings.create(
    name="Custom Consulting",
    price=3500,
    fulfillment_url="https://yourapp.com/webhooks/listbee/fulfill",
    checkout_schema=[
        CheckoutField.text("brief", label="Project Brief", sort_order=0),
    ],
)
listing = client.listings.publish(listing.id)
```

Using an environment variable instead:

```bash
export LISTBEE_API_KEY="lb_..."
```

```python
from listbee import ListBee

from listbee import ListBee, Deliverable

client = ListBee()  # reads LISTBEE_API_KEY automatically

listing = client.listings.create_complete(
    name="SEO Playbook",
    price=2900,
    deliverables=[Deliverable.url("https://example.com/seo-playbook.pdf")],
)
listing = client.listings.publish(listing.id)
print(listing.url)
```

## Authentication

### Bootstrap (programmatic account creation)

Use the 3-step bootstrap flow to create a new account and obtain an API key entirely via the SDK — no Console visit required.

```python
from listbee import ListBee

# No API key needed for bootstrap
client = ListBee(api_key="")

# Step 1 — send OTP to email
session = client.bootstrap.start(email="seller@example.com")
print(session.session)   # sess_abc123

# Step 2 — verify OTP from email
verified = client.bootstrap.verify(session=session.session, code="123456")
print(verified.verified)   # True

# Step 3 — create store and get API key (shown once — save immediately)
store = client.bootstrap.create_store(
    session=verified.session,
    store_name="Acme Agency",
)
print(store.api_key)   # lb_... — store this securely
print(store.url)       # https://buy.listbee.so/acme-agency
```

The `api_key` in the `StoreResponse` is returned **only once**. Store it in your secrets manager before continuing.

### Existing key

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

API keys start with `lb_`.

## Resources

### Listings

```python
from listbee import ListBee

client = ListBee(api_key="lb_...")

# Create — managed delivery (ListBee delivers pre-attached deliverables)
# Listings start as drafts. Attach deliverables then publish.
listing = client.listings.create(
    name="SEO Playbook",
    price=2900,       # $29.00 in cents
)

# Create — external fulfillment (your system handles delivery via fulfillment_url)
from listbee import CheckoutField

listing = client.listings.create(
    name="Custom Consulting",
    price=3500,
    fulfillment_url="https://yourapp.com/webhooks/listbee/fulfill",
    checkout_schema=[
        CheckoutField.text("brief", label="Project Brief", sort_order=0),
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
from listbee import Deliverable

client.listings.set_deliverables(
    listing.id,
    deliverables=[Deliverable.url("https://example.com/seo-playbook.pdf")],
)
listing = client.listings.publish(listing.id)
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

# Update fulfillment URL and checkout schema
from listbee import CheckoutField

updated = client.listings.update(
    "r7kq2xy9",
    fulfillment_url="https://yourapp.com/webhooks/listbee/fulfill",
    checkout_schema=[
        CheckoutField.text("notes", label="Special Instructions", sort_order=0),
    ],
)

# Raw dicts also accepted for backward compatibility:
updated = client.listings.update(
    "r7kq2xy9",
    checkout_schema=[
        {"key": "notes", "label": "Special Instructions", "type": "text", "sort_order": 0},
    ],
)

# Set deliverables on a draft listing (one or more)
client.listings.set_deliverables(
    "r7kq2xy9",
    deliverables=[
        Deliverable.url("https://example.com/seo-playbook.pdf"),
    ],
)

# Remove all deliverables from a draft listing
client.listings.remove_deliverables("r7kq2xy9")

# Add a single deliverable
client.listings.add_deliverable("r7kq2xy9", Deliverable.url("https://example.com/playbook.pdf"))
client.listings.add_deliverable("r7kq2xy9", Deliverable.text("Your license key: XXXX-XXXX"))

with open("guide.pdf", "rb") as f:
    file = client.files.upload(file=f, filename="guide.pdf")
client.listings.add_deliverable("r7kq2xy9", Deliverable.from_token(file.id))

# Remove a single deliverable by del_ ID
client.listings.remove_deliverable("r7kq2xy9", "del_4hR9nK2mQ7tV5wX1")

# Create a listing and attach deliverables in one call
listing = client.listings.create_complete(
    name="SEO Playbook",
    price=2900,
    deliverables=[
        Deliverable.url("https://example.com/seo-playbook.pdf"),
    ],
)
listing = client.listings.publish(listing.id)

# Publish a draft listing — makes it live and purchasable
listing = client.listings.publish("r7kq2xy9")
print(listing.status)    # "published"

# Set cover image — accepts a file_ token, image URL, bytes, or BinaryIO
# From a URL (fetched, validated as image, uploaded, then applied):
listing = client.listings.set_cover("lst_r7kq2xy9", "https://example.com/cover.jpg")

# From local file bytes:
with open("cover.png", "rb") as f:
    listing = client.listings.set_cover("lst_r7kq2xy9", f)

# From a pre-uploaded file token:
file = client.files.upload(file=("cover.jpg", img_bytes, "image/jpeg"), purpose="cover")
listing = client.listings.update("lst_r7kq2xy9", cover_url=file.id)

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
print(order.payment_status)       # "unpaid" | "paid" | "refunded"
print(order.has_deliverables)     # True if deliverables are attached
print(order.actions)              # list of available actions (with priority)
print(order.listing_snapshot)     # listing data at time of purchase
print(order.seller_snapshot)      # seller data at time of purchase
print(order.paid_at)              # when payment was confirmed

# Fulfill a generated order — push deliverables for ListBee to deliver
order = client.orders.fulfill("ord_9xM4kP7nR2qT5wY1")
print(order.status)               # "fulfilled"

# Fulfill with dynamic content — push deliverables for ListBee to deliver
from listbee import Deliverable

order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[
        Deliverable.text("Here is your personalized report..."),
    ],
)
print(order.status)               # "fulfilled"

# Fulfill with a URL
order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[
        Deliverable.url("https://example.com/generated-report.pdf"),
    ],
)

# Refund an order — issues a full refund and marks order canceled
order = client.orders.refund("ord_9xM4kP7nR2qT5wY1")
print(order.status)               # "canceled"
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

# Update account settings
client.account.update(ga_measurement_id="G-XXXXXXXXXX")
client.account.update(notify_orders=False)
client.account.update(ga_measurement_id=None)  # clear GA ID

# Delete account — irreversible
client.account.delete()
```

Brand information (display name, bio, avatar, slug) lives on the Store — see the [Store](#store) section.

### Store

```python
store = client.store.get()
print(store.id)            # st_7kQ2xY9mN3pR5tW1vB8a
print(store.display_name)  # Acme Agency
print(store.slug)          # acme-agency
print(store.url)           # https://buy.listbee.so/acme-agency
print(store.has_avatar)    # True when an avatar has been uploaded
print(store.readiness.sellable)

# Update brand information
store = client.store.update(display_name="New Agency Name")
store = client.store.update(bio="We help teams ship faster.")
store = client.store.update(slug="new-slug")

# Set avatar — one-step helper: accepts a file token, URL, bytes, or BinaryIO
# From a URL (fetched, validated as image, uploaded, then applied):
store = client.store.set_avatar("https://example.com/avatar.png")

# From local file bytes:
with open("avatar.png", "rb") as f:
    store = client.store.set_avatar(f)

# From a pre-uploaded file token:
file = client.files.upload(file=("avatar.png", img_bytes, "image/png"), purpose="avatar")
store = client.store.update(avatar=file.id)
```

### Customers

```python
# List all customers (buyers who have placed orders)
for customer in client.customers.list():
    print(customer.email, customer.total_orders)

# Get a customer by ID
customer = client.customers.get("acc_4hR9nK2mQ7tV5wX1")
print(customer.email)
print(customer.total_spent)    # total amount in cents
print(customer.total_orders)
```

### Files

```python
from listbee import Deliverable

# Upload a file as a deliverable (default purpose)
with open("playbook.pdf", "rb") as f:
    content = f.read()
file = client.files.upload(file=("playbook.pdf", content, "application/pdf"))
print(file.id)      # file_ token — valid for 24 hours
print(file.purpose) # "deliverable"

# Upload with explicit purpose
cover = client.files.upload(
    file=("cover.jpg", img_bytes, "image/jpeg"),
    purpose="cover",       # "deliverable" | "cover" | "avatar"
)
avatar = client.files.upload(
    file=("avatar.png", img_bytes, "image/png"),
    purpose="avatar",
)

# Then attach to a listing using the uploaded file token
client.listings.set_deliverables(
    "lst_r7kq2xy9",
    deliverables=[Deliverable.from_token(file.id)],
)

# Or use set_cover / set_avatar convenience helpers (handle upload automatically)
client.listings.set_cover("lst_r7kq2xy9", cover.id)   # token
client.store.set_avatar(avatar.id)                      # token
```

### Stripe

```python
# Generate a Stripe Connect onboarding link
connect = client.stripe.connect()
print(connect.url)  # redirect seller here

# Disconnect Stripe
client.stripe.disconnect()
```

### Utility

```python
# Check API connectivity
response = client.utility.ping()
print(response.status)  # "ok"

# List available pricing plans (no authentication required)
plans = client.utility.plans()
for plan in plans.data:
    print(f"{plan.name}: ${plan.price_monthly / 100}/month (fee: {plan.fee_rate})")
```

## Fulfillment Modes

ListBee supports two fulfillment modes determined by the listing's deliverables and `fulfillment_url`.

**Managed** — ListBee delivers pre-attached digital content (files, URLs, text) automatically on payment. Attach deliverables to the listing before publishing.

```python
from listbee import Deliverable

# One-shot: create listing + attach deliverables + publish
listing = client.listings.create_complete(
    name="SEO Playbook",
    price=2900,
    deliverables=[
        Deliverable.url("https://example.com/seo-playbook.pdf"),
    ],
)
listing = client.listings.publish(listing.id)

# Add or remove individual deliverables after creation
client.listings.add_deliverable(listing.id, Deliverable.text("Bonus: license key XXXX-XXXX"))
client.listings.remove_deliverable(listing.id, "del_4hR9nK2mQ7tV5wX1")
```

Upload a file and use it as a deliverable:

```python
with open("playbook.pdf", "rb") as f:
    file = client.files.upload(file=f, filename="playbook.pdf")
client.listings.add_deliverable(listing.id, Deliverable.from_token(file.id))
```

**External** — Set `fulfillment_url` and ListBee POSTs the order to your URL after payment. Your system handles delivery. Use for physical goods, AI-generated content, services, or anything that requires custom logic.

```python
from listbee import CheckoutField, Deliverable

# AI-generated content — receive order, generate, push back via fulfill()
listing = client.listings.create(
    name="Custom AI Report",
    price=4900,
    fulfillment_url="https://yourapp.com/webhooks/listbee/fulfill",
    checkout_schema=[
        CheckoutField.text("topic", label="Report Topic", sort_order=0),
    ],
)
listing = client.listings.publish(listing.id)

# When your endpoint receives the order, generate content and push back:
order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[
        Deliverable.text("Your personalized report..."),
    ],
)
```

Use `order.has_deliverables` and `order.actions` to branch post-payment logic:

```python
order = client.orders.get("ord_9xM4kP7nR2qT5wY1")
if order.has_deliverables:
    # ListBee has deliverables ready for the buyer
    pass
if order.actions:
    # There are actions to take — check priority
    for action in order.actions:
        print(f"{action.priority}: {action.code} — {action.message}")
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
| `configure_webhook` | Listing with `fulfillment_url` needs a webhook endpoint configured |
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

## Utility

Verify API connectivity and that your API key is valid:

```python
response = client.utility.ping()
print(response.status)  # "ok"
```

For async:

```python
response = await client.utility.ping()
print(response.status)  # "ok"
```

## Pagination

`listings.list()` and `orders.list()` return a cursor-paginated page that auto-fetches subsequent pages when iterated.

List endpoints return **slim summary objects** (`ListingSummary` / `OrderSummary`) with core fields for display. Call `.get(id)` to retrieve the full object with all fields.

```python
# Auto-pagination — iterates all pages transparently
# Each item is a ListingSummary (slim: id, slug, name, price, status, url, ...)
for listing in client.listings.list():
    print(listing.name, listing.url)

# Need full details? Fetch by ID
full = client.listings.get(listing.id)
print(full.deliverables, full.reviews, full.faqs)

# Manual page control — access current page directly
page = client.listings.list(limit=10)
print(page.data)       # list of ListingSummary on this page
print(page.has_more)   # True if more pages exist
print(page.cursor)     # cursor string for the next page

# Fetch next page manually
if page.has_more:
    next_page = client.listings.list(limit=10, cursor=page.cursor)
    print(next_page.data)

# Collect all pages into a single list
all_listings = page.to_list(limit=None)
print(len(all_listings))  # total items across all pages
```

## Helper Methods & Properties

The SDK includes convenience helpers for common patterns and state checks.

### Order State Helpers

```python
order = client.orders.get("ord_9xM4kP7nR2qT5wY1")

# Payment state checkers
if order.is_paid:
    print("Order has been paid")
if order.is_refunded:
    print("Order was refunded")
if order.is_disputed:
    print("Order is under dispute")

# Fulfillment state checkers
if order.needs_fulfillment:
    print("Call orders.fulfill() to push content")
if order.is_terminal:
    print("Order is in a final state (fulfilled, canceled, or failed)")

# Fulfill a paid order — push content for ListBee to deliver
if order.needs_fulfillment:
    order = client.orders.fulfill(
        order.id,
        deliverables=[Deliverable.text("Your generated report...")]
    )
```

### Listing State Helpers

```python
listing = client.listings.get("r7kq2xy9")

# Publication state
if listing.is_draft:
    print("Listing is not yet publishable")
if listing.is_published:
    print("Listing is live and purchasable")

# Stock state
if listing.is_in_stock:
    print("Stock available for purchase")

# Content state
if listing.has_deliverables:
    print(f"Listing has {len(listing.deliverables)} deliverables")

# Checkout link
print(f"Share: {listing.checkout_url}")
```

### Readiness System Helpers

```python
account = client.account.get()

# Quick readiness check
if account.is_ready:
    print("Account is fully operational")

# Get the highest-priority action
if not account.is_ready:
    action = account.next_action
    print(f"Action needed: {action.code} -> {action.message}")

# Filter actions by kind
api_actions = account.actions_by_kind("api")
manual_actions = account.actions_by_kind("human")

for action in api_actions:
    print(f"Can be fixed via API: {action.code}")
    print(f"  Endpoint: {action.resolve.endpoint}")
    print(f"  Method: {action.resolve.method}")
```

Similar helpers on `ListingReadiness`:

```python
listing = client.listings.get("r7kq2xy9")
if not listing.readiness.is_ready:
    next_action = listing.readiness.next_action
    print(f"Next: {next_action.code}")
```

### Price Formatting

```python
from listbee import format_price, to_minor, from_minor

# Format cents as a decimal price
price_str = format_price(2900)  # "$29.00"

# Convert decimal to cents
cents = to_minor(29.00)  # 2900

# Convert cents to decimal
decimal = from_minor(2900)  # 29.00
```

### Webhook Parsing & Verification

Parse and verify webhook events in one step:

```python
from listbee import parse_webhook_event, WebhookVerificationError

# In your webhook handler
payload = request.body  # raw bytes
signature = request.headers["listbee-signature"]
secret = "whsec_..."    # from webhook.secret

try:
    event = parse_webhook_event(payload=payload, signature=signature, secret=secret)
    print(f"Event: {event.type}")
    print(f"Order ID: {event.data.id}")
except WebhookVerificationError:
    # Signature invalid — reject the request
    return Response(status_code=401)
```

`parse_webhook_event` automatically verifies the signature and parses the JSON payload. Raises `WebhookVerificationError` if verification fails.

Or verify and parse separately:

```python
from listbee import verify_signature, WebhookVerificationError
import json

payload = request.body
signature = request.headers["listbee-signature"]

try:
    verify_signature(payload=payload, signature=signature, secret=secret)
except WebhookVerificationError:
    return Response(status_code=401)

event = json.loads(payload)
```

## Client Configuration

### Per-Call Options

Override defaults for a single request:

```python
# Custom timeout for this call
listing = client.listings.create(
    name="Heavy image processing",
    price=2900,
    cover_url="https://example.com/large.jpg",
    timeout=180.0,  # 3 minutes, overrides default 120s for create()
)

# Custom retries for this call
order = client.orders.get(
    "ord_9xM4kP7nR2qT5wY1",
    max_retries=5,  # retry more aggressively on this request
)
```

### Client-Level Options

```python
from listbee import ListBee

client = ListBee(
    api_key="lb_...",
    timeout=60.0,           # default request timeout
    max_retries=3,          # retries on 429/500/502/503/504
    base_url="https://api.listbee.so",  # default; override for testing
)
```

### Custom HTTP Client

Use a custom `httpx.Client` or `httpx.AsyncClient`:

```python
import httpx
from listbee import ListBee, DefaultHttpxClient

# Custom sync client with extra configuration
http_client = httpx.Client(
    timeout=120.0,
    limits=httpx.Limits(max_keepalive_connections=10),
    headers={"User-Agent": "my-app/1.0"},
)

client = ListBee(
    api_key="lb_...",
    http_client=DefaultHttpxClient(client=http_client),
)
```

For async:

```python
import httpx
from listbee import AsyncListBee, DefaultAsyncHttpxClient

http_client = httpx.AsyncClient(
    timeout=120.0,
    limits=httpx.Limits(max_keepalive_connections=10),
)

client = AsyncListBee(
    api_key="lb_...",
    http_client=DefaultAsyncHttpxClient(client=http_client),
)
```

### Raw Response Access

Access HTTP response headers, status, and request metadata:

```python
from listbee import ListBee

client = ListBee(api_key="lb_...")

# Get the raw response wrapper
response = client.with_raw_response().account.get()

# Access parsed model
print(response.parsed.email)

# Access raw HTTP response
print(response.response.status_code)
print(response.response.headers["x-request-id"])
print(response.response.headers["x-ratelimit-remaining"])
```

This works on any resource method:

```python
response = client.with_raw_response().listings.get("r7kq2xy9")
print(f"Status: {response.response.status_code}")
print(f"Request ID: {response.response.headers.get('x-request-id')}")
print(f"Listing: {response.parsed.name}")
```

## Action Resolution (Advanced)

Automatically resolve readiness actions via API:

```python
from listbee import resolve_action

account = client.account.get()
if not account.is_ready:
    action = account.next_action
    
    # Resolve this action (if it's an API action)
    if action.kind == "api":
        result = resolve_action(client, action)
        # Handles action code, calls appropriate endpoint
```

For async:

```python
from listbee import resolve_action_async

account = await client.account.get()
result = await resolve_action_async(client, action)
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
from listbee import AsyncListBee, Deliverable

async def main():
    client = AsyncListBee(api_key="lb_...")

    # Create a listing, attach deliverable, publish
    listing = await client.listings.create_complete(
        name="SEO Playbook",
        price=2900,
        deliverables=[Deliverable.url("https://example.com/seo-playbook.pdf")],
    )
    listing = await client.listings.publish(listing.id)
    print(listing.url)

    # Iterate all listings
    async for listing in await client.listings.list():
        print(listing.slug, listing.name)

    # Filter paid orders
    async for order in await client.orders.list(status="paid"):
        print(order.id)

    # Fulfill an order (async)
    order = await client.orders.fulfill(
        "ord_9xM4kP7nR2qT5wY1",
        deliverables=[Deliverable.text("Generated content here")],
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
    ListingResponse,   # full listing (returned by get())
    ListingSummary,    # slim listing (returned by list())
    OrderResponse,     # full order (returned by get())
    OrderSummary,      # slim order (returned by list())
    WebhookResponse,
    AccountResponse,
    StoreResponse,
    StoreReadiness,
    BootstrapResponse,
    BootstrapVerifyResponse,
    CustomerResponse,
    FileResponse,
    ListingReadiness,
    AccountReadiness,
    Action,
    ActionResolve,
    Review,
    FaqItem,
    CursorPage,
    CheckoutFieldResponse,

    # Builder classes
    CheckoutField,       # input class: .text() | .select() | .date()
    Deliverable,         # input class: .file() | .url() | .text() | .from_token()

    # Enums
    ActionPriority,      # "required" | "suggested"
    DeliverableType,     # "file" | "url" | "text"
    PaymentStatus,       # "unpaid" | "paid" | "refunded"
    CheckoutFieldType,   # "text" | "select" | "date"
    BlurMode,            # "auto" | "true" | "false"
    ListingStatus,       # "draft" | "published"
    OrderStatus,         # "pending" | "paid" | "fulfilled" | "canceled" | "failed"
    WebhookEventType,    # "order.paid" | "order.fulfilled" | "order.refunded" | ...
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
    PartialCreationError,  # listing created but deliverable attachment failed
)
```

Use enums to avoid magic strings:

```python
from listbee import ActionPriority, DeliverableType, PaymentStatus, ActionCode, ActionKind, WebhookEventType

# Check if managed delivery has been configured
if listing.has_deliverables:
    print(f"Delivers {listing.deliverables[0].type} file")

# Check for required actions on an order
if order.actions:
    required = [a for a in order.actions if a.priority == ActionPriority.REQUIRED]
    for action in required:
        print(f"Required: {action.code} — {action.message}")

# Subscribe to specific events
webhook = client.webhooks.create(
    name="Orders only",
    url="https://example.com/hooks",
    events=[
        WebhookEventType.ORDER_PAID,
        WebhookEventType.ORDER_FULFILLED,
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

## Migration Guide

### From v0.16.x to Unreleased

**Breaking Change: Store `avatar_url` field removed — use `has_avatar` bool**

`StoreResponse.avatar_url` is replaced by `StoreResponse.has_avatar` (bool). To set the avatar, upload a file token and pass it to `update(avatar=...)` or use the `set_avatar()` helper.

```python
# Old (v0.16.x)
store = client.store.get()
print(store.avatar_url)   # URL or None

client.store.update(avatar_url="https://example.com/avatar.png")

# New
store = client.store.get()
print(store.has_avatar)   # True / False

# One-step helper: URL, bytes, BinaryIO, or file_ token
client.store.set_avatar("https://example.com/avatar.png")
client.store.set_avatar(open("avatar.png", "rb"))

# Or upload manually and pass the token
file = client.files.upload(file=("avatar.png", img_bytes, "image/png"), purpose="avatar")
client.store.update(avatar=file.id)
```

**New: `set_cover()` on listings — one-step cover image upload**

```python
# Old: upload then update manually
file = client.files.upload(file=("cover.jpg", img_bytes, "image/jpeg"))
client.listings.update("lst_abc", cover_url=file.id)

# New: one-step helper
client.listings.set_cover("lst_abc", "https://example.com/cover.jpg")
client.listings.set_cover("lst_abc", open("cover.jpg", "rb"))
client.listings.set_cover("lst_abc", img_bytes)
```

### From v0.15.x to v0.16.x

**Breaking Change: API Keys removed — use Bootstrap**

The `client.api_keys` resource has been removed. Use the bootstrap flow to create accounts and obtain API keys programmatically.

```python
# Old (v0.15.x)
new_key = client.api_keys.create(name="CI pipeline")
print(new_key.key)

# New (v0.16.x) — bootstrap creates the account and issues the key
client = ListBee(api_key="")
session = client.bootstrap.start(email="seller@example.com")
verified = client.bootstrap.verify(session=session.session, code="123456")
store = client.bootstrap.create_store(session=verified.session, store_name="Acme Agency")
print(store.api_key)  # lb_... — save immediately
```

**Breaking Change: Brand fields moved from Account to Store**

`display_name`, `bio`, and `has_avatar` are no longer on `AccountResponse`. They now live on `StoreResponse`.

```python
# Old (v0.15.x)
account = client.account.get()
print(account.display_name)

client.account.update(display_name="New Name", bio="Short bio")

# New (v0.16.x)
store = client.store.get()
print(store.display_name)

client.store.update(display_name="New Name", bio="Short bio")
```

### From v0.14.x to v0.15.x

**Breaking Change: Content Type → Implicit Fulfillment Model**

The `content_type` field has been removed. Fulfillment is now determined implicitly:
- Listings with deliverables attached → ListBee manages delivery
- Listings with `fulfillment_url` set → Your system handles delivery

```python
# Old (v0.14.x)
listing = client.listings.create(
    name="Report",
    price=2900,
    content_type="static",
)

# New (v0.15.x)
listing = client.listings.create(
    name="Report",
    price=2900,
    # Attach deliverables after creation, or use create_complete()
)

# Old (external fulfillment)
listing = client.listings.create(
    name="Custom Service",
    price=2900,
    content_type="webhook",
)

# New (external fulfillment)
listing = client.listings.create(
    name="Custom Service",
    price=2900,
    fulfillment_url="https://yourapp.com/webhooks/listbee/fulfill",
)
```

**Changed: Order fields**

```python
order = client.orders.get("ord_...")

# Removed in v0.15.x
# order.content_type     — removed
# order.handed_off_at    — removed

# New in v0.15.x
print(order.has_deliverables)  # True if deliverables are attached
print(order.actions)           # list of available actions with priority
```

**Changed: OrderStatus**

`PROCESSING` and `HANDED_OFF` values removed from `OrderStatus`. Lifecycle is now `PENDING → PAID → FULFILLED`.

### From v0.13.x to v0.14.0

**Breaking Change: Fulfillment → Content Type**

The fulfillment concept was replaced with content types in v0.14.0. See v0.14.0 release notes for details.

### From v0.12.x to v0.13.x

**Breaking Change: Removed signup resource**

Account creation is now handled via the ListBee Console. The `client.signup` resource has been removed.

```python
# Old (v0.12.x)
response = client.signup.send_otp("seller@example.com")
token = client.signup.verify_otp("seller@example.com", "123456")

# New (v0.13.x)
# Use the Console at https://console.listbee.so to create accounts
# Then use API key for subsequent API calls
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
