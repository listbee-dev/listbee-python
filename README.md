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
| Bootstrap | start, verify, poll, run |
| Listings | create, get, list, update, delete, publish, unpublish, archive |
| Orders | get, list, fulfill, refund, redeliver |
| Events | list |
| ApiKeys | self_revoke |
| Account | get, update, delete |
| Stripe | connect, disconnect |
| Utility | ping, plans |

```python
from listbee import ListBee, Deliverable

client = ListBee(api_key="lb_...")

# Managed mode — ListBee delivers the attached deliverable automatically on payment
result = client.listings.create(
    name="SEO Playbook",
    price=2900,
    deliverable=Deliverable.url("https://example.com/seo-playbook.pdf"),
)
# result is a ListingCreateResponse envelope
print(result.signing_secret)   # store immediately — shown once!
print(result.listing.id)       # lst_...
listing = client.listings.publish(result.listing.id)
print(listing.url)   # https://buy.listbee.so/l/lst_.../seo-playbook

# Async mode — your agent receives order.paid and calls fulfill() to push content
from listbee import CheckoutField

result = client.listings.create(
    name="Custom Consulting",
    price=3500,
    agent_callback_url="https://yourapp.com/webhooks/listbee",
    checkout_schema=[
        CheckoutField.text("brief", label="Project Brief", sort_order=0),
    ],
)
listing = client.listings.publish(result.listing.id)
```

Using an environment variable instead:

```bash
export LISTBEE_API_KEY="lb_..."
```

```python
from listbee import ListBee, Deliverable

client = ListBee()  # reads LISTBEE_API_KEY automatically

result = client.listings.create(
    name="SEO Playbook",
    price=2900,
    deliverable=Deliverable.url("https://example.com/seo-playbook.pdf"),
)
listing = client.listings.publish(result.listing.id)
print(listing.url)
```

## Authentication

### Bootstrap (programmatic account creation)

Use the 2-step bootstrap flow to create a new account and obtain an API key entirely via the SDK — no Console visit required.

```python
from listbee import ListBee

# No API key needed for bootstrap
client = ListBee(api_key="")

# Step 1 — send OTP to email
session = client.bootstrap.start(email="seller@example.com")
print(session.bootstrap_token)   # bst_abc123def456

# Step 2 — verify OTP and get API key immediately
result = client.bootstrap.verify(
    bootstrap_token=session.bootstrap_token,
    otp_code="123456",   # 6-digit code from email
)
print(result.api_key)       # lb_... — store this securely (shown once)
print(result.account_id)    # acc_01J3K4M5N6P7Q8R9S0T1U2V3W4
print(result.readiness.operational)   # True if Stripe already connected
```

The `api_key` in the `BootstrapVerifyResponse` is shown **once** — store it in your secrets manager immediately.

If Stripe Connect onboarding is required, `stripe_onboarding_url` will be non-null and `readiness.operational` will be `False`. Poll `bootstrap.poll(account_id)` until `ready` is `True`.

**High-level helper (recommended for agents)**

```python
# Handles the full flow: start → OTP → verify → Stripe onboarding → poll
api_key = client.bootstrap.run(
    "seller@example.com",
    on_otp=lambda: input("Enter OTP: ").strip(),
    on_human_action=lambda url: print(f"Complete Stripe setup: {url}"),
    poll_interval=5.0,
)
# api_key is ready to use
```

**Manual poll loop (if not using run())**

```python
import time

result = client.bootstrap.verify(
    bootstrap_token=session.bootstrap_token,
    otp_code="123456",
)
api_key = result.api_key

if not result.readiness.operational:
    print(f"Complete Stripe setup: {result.stripe_onboarding_url}")
    while True:
        poll = client.bootstrap.poll(result.account_id)
        if poll.ready:
            break
        time.sleep(5)
```

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
from listbee import ListBee, Deliverable

client = ListBee(api_key="lb_...")

# Create — MANAGED mode (ListBee delivers the deliverable automatically on payment)
# POST /v1/listings returns a ListingCreateResponse envelope (not a flat listing)
result = client.listings.create(
    name="SEO Playbook",
    price=2900,       # $29.00 in cents
    deliverable=Deliverable.url("https://example.com/seo-playbook.pdf"),
)
# result.signing_secret — store this immediately, shown only once
# result.listing — ListingBase object with all listing fields
print(result.signing_secret)     # lbs_sk_... — webhook signing secret, store now!
print(result.listing.id)         # lst_...
print(result.listing.url)        # https://buy.listbee.so/l/lst_.../seo-playbook
print(result.listing.currency)   # usd
print(result.listing.fulfillment_mode)  # MANAGED (computed from deliverable presence)

listing = client.listings.publish(result.listing.id)
print(listing.url)          # https://buy.listbee.so/l/lst_.../seo-playbook
print(listing.stats.views)  # 0 — stats included in GET/PUT responses

# Create — ASYNC mode (agent receives order.paid via agent_callback_url and calls fulfill())
from listbee import CheckoutField

result = client.listings.create(
    name="Custom Consulting",
    price=3500,
    agent_callback_url="https://yourapp.com/webhooks/listbee",
    checkout_schema=[
        CheckoutField.text("brief", label="Project Brief", sort_order=0),
    ],
)
# fulfillment_mode is ASYNC automatically (no deliverable attached)
print(result.listing.fulfillment_mode)  # ASYNC

# Create — all optional params
result = client.listings.create(
    name="SEO Playbook 2026",
    price=2900,
    deliverable=Deliverable.text("License key: ABCD-1234"),
    image_url="https://cdn.example.com/covers/seo-playbook.jpg",
    currency="usd",                    # ISO 4217 lowercase (defaults to account currency)
    description="A comprehensive guide to modern SEO techniques.",
    tagline="Updated for 2026 algorithm changes",
    highlights=["50+ pages", "Actionable tips", "Free updates"],
    cta="Get Instant Access",          # buy button text; defaults to "Buy Now"
    compare_at_price=3900,             # strikethrough price
    badges=["Limited time", "Best seller"],
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
print(result.listing.id)    # lst_...

# Get by ID — returns ListingDetailResponse (includes stats)
listing = client.listings.get("lst_r7kq2xy9m3pR5tW1")
print(listing.stats.views)        # page view count
print(listing.stats.purchases)    # purchase count
print(listing.stats.gmv_minor)    # gross merchandise value in cents

# Deliverable shape on response — {"type": "url"|"text", "content": "..."}
if listing.deliverable:
    print(listing.deliverable.type)     # "url" or "text"
    print(listing.deliverable.content)  # the URL or text (redacted on public reads)

# Readiness — use buyable (not sellable)
if not listing.readiness.buyable:
    print(listing.readiness.next)    # highest-priority action code

# List — auto-paginates, each item is ListingSummary
for listing in client.listings.list():
    print(listing.name, listing.url)          # url is composite /l/{id}/{slug}
    print(listing.image_url, listing.currency)

# Update — partial updates, returns ListingDetailResponse
updated = client.listings.update(
    "lst_r7kq2xy9m3pR5tW1",
    name="SEO Playbook 2026 Updated",
    price=3900,
    image_url="https://cdn.example.com/new-cover.jpg",
)

# Update deliverable
updated = client.listings.update(
    "lst_r7kq2xy9m3pR5tW1",
    deliverable=Deliverable.url("https://example.com/new-version.pdf"),
)

# Rotate signing secret — returns RotateSigningSecretResponse
from listbee import RotateSigningSecretResponse

result = client.listings.update("lst_r7kq2xy9m3pR5tW1", signing_secret="rotate")
if isinstance(result, RotateSigningSecretResponse):
    print(result.signing_secret)    # new secret — store immediately

# Update checkout schema
updated = client.listings.update(
    "lst_r7kq2xy9m3pR5tW1",
    checkout_schema=[
        CheckoutField.text("notes", label="Special Instructions", sort_order=0),
    ],
)

# Publish a draft listing — makes it live and purchasable
listing = client.listings.publish("lst_r7kq2xy9m3pR5tW1")
print(listing.status)    # "published"

# Unpublish a published listing — moves it back to draft
listing = client.listings.unpublish("lst_r7kq2xy9m3pR5tW1")
print(listing.status)    # "draft"

# Archive a listing — permanently removes it from public view
listing = client.listings.archive("lst_r7kq2xy9m3pR5tW1")
print(listing.status)    # "archived"
print(listing.is_archived)   # True

# Delete
client.listings.delete("lst_r7kq2xy9m3pR5tW1")
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
print(order.deliverable)          # single deliverable after fulfillment (or None)
print(order.unlock_url)           # permanent bearer link for buyer to access content
print(order.metadata)             # key-value pairs attached to the order
print(order.actions)              # list of available actions (with priority)
print(order.listing_snapshot)     # listing data at time of purchase
print(order.seller_snapshot)      # seller data at time of purchase
print(order.paid_at)              # when payment was confirmed

# Fulfill an async-mode order — push generated content to ListBee for delivery
from listbee import Deliverable

order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverable=Deliverable.text("Here is your personalized report..."),
    metadata={"generated_by": "my-agent", "version": "1"},
)
print(order.status)               # "fulfilled"
print(order.unlock_url)           # buyer's download link

# Fulfill with a URL
order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverable=Deliverable.url("https://example.com/generated-report.pdf"),
)

# Close out an external-fulfillment order without pushing content
order = client.orders.fulfill("ord_9xM4kP7nR2qT5wY1")

# Refund an order — issues a full refund
order = client.orders.refund("ord_9xM4kP7nR2qT5wY1")

# Re-queue webhook delivery (useful for retrying failed agent_callback_url deliveries)
ack = client.orders.redeliver("ord_9xM4kP7nR2qT5wY1")
print(ack.scheduled_attempts)    # number of re-delivery attempts queued
```

### Events

```python
# List all events (newest first, cursor-paginated)
for event in client.events.list():
    print(event.id, event.type, event.created_at)

# Filter by type
for event in client.events.list(type="order.paid"):
    print(event.order_id, event.data)

# Filter by listing or order
for event in client.events.list(listing_id="lst_abc123"):
    print(event.type, event.data)

for event in client.events.list(order_id="ord_9xM4kP7nR2qT5wY1"):
    print(event.type)

# Paginate
page = client.events.list(limit=10)
if page.has_more:
    next_page = client.events.list(cursor=page.cursor)
```

### ApiKeys

```python
# Self-revoke the calling API key — immediately invalidates it
result = client.api_keys.self_revoke()
print(result.id)           # lbk_...
print(result.revoked_at)   # datetime when revoked
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
client.account.update(events_callback_url="https://yourapp.com/events")
client.account.update(ga_measurement_id=None)  # clear GA ID

# Delete account — irreversible
client.account.delete()
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

ListBee supports two fulfillment modes. `fulfillment_mode` is **computed server-side** from whether a deliverable is attached — you do not set it explicitly.

**MANAGED** — ListBee delivers a pre-attached digital deliverable (URL or text) automatically when the buyer pays. Set by attaching a `deliverable` to the listing.

```python
from listbee import Deliverable

# Attach a URL deliverable — fulfillment_mode becomes MANAGED automatically
result = client.listings.create(
    name="SEO Playbook",
    price=2900,
    deliverable=Deliverable.url("https://example.com/seo-playbook.pdf"),
)
listing = client.listings.publish(result.listing.id)

# Attach a text deliverable (license key, access code, etc.)
result = client.listings.create(
    name="Plugin License",
    price=4900,
    deliverable=Deliverable.text("Your license key: ABCD-1234-EFGH-5678"),
)
```

**ASYNC** — ListBee fires an `order.paid` event to your `agent_callback_url`. Your agent generates content and pushes it back via `orders.fulfill()`. Use for AI-generated content, physical goods, services, or anything requiring custom logic. Set by omitting the `deliverable`.

```python
from listbee import CheckoutField, Deliverable

# AI-generated content — no deliverable = ASYNC mode automatically
result = client.listings.create(
    name="Custom AI Report",
    price=4900,
    agent_callback_url="https://yourapp.com/webhooks/listbee",
    checkout_schema=[
        CheckoutField.text("topic", label="Report Topic", sort_order=0),
    ],
)
listing = client.listings.publish(result.listing.id)

# When your endpoint receives the order.paid event, generate and push back:
order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverable=Deliverable.text("Your personalized report..."),
)
```

Use `order.actions` to check what's needed after payment:

```python
order = client.orders.get("ord_9xM4kP7nR2qT5wY1")
if order.actions:
    for action in order.actions:
        print(f"{action.priority}: {action.code} — {action.message}")
```

## Readiness System

Every listing and account includes a `readiness` field that tells you whether it can currently accept payments.

- `listing.readiness.buyable` — `True` when buyers can complete a purchase right now
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
listing = client.listings.get("lst_r7kq2xy9m3pR5tW1")
if not listing.readiness.buyable:
    for action in listing.readiness.actions:
        print(action.code, action.message)
    print(f"Next: {listing.readiness.next}")
```

**Action codes:**

| Code | Meaning |
|------|---------|
| `otp_verification_pending` | OTP has been sent but not yet verified |
| `stripe_connect_required` | No Stripe account connected — start Connect onboarding |
| `stripe_charges_disabled` | Stripe charges disabled — complete Stripe onboarding |
| `account_deleted` | Account has been deleted |
| `listing_unpublished` | Listing is a draft — publish to make it purchasable |
| `listing_deliverable_missing` | Static-mode listing has no deliverable attached |
| `fulfillment_pending` | Async-mode order is awaiting fulfillment via `orders.fulfill()` |
| `dispute_open` | Order has an open dispute requiring attention |

## Webhook Signature Verification

Verify that incoming webhook requests genuinely come from ListBee before processing them.

Each listing has a signing secret returned once at creation time (`ListingCreateResponse.signing_secret`). Store it in your secrets manager. To rotate, call `listings.update(id, signing_secret="rotate")`.

```python
from listbee import verify_signature, WebhookVerificationError

# In your webhook handler (e.g. FastAPI, Flask, Django):
payload = request.body      # raw bytes — do not parse first
signature = request.headers["listbee-signature"]
secret = "whsec_..."        # listing signing secret

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
# Each item is a ListingSummary (slim: id, url, name, price, currency, image_url, status, ...)
for listing in client.listings.list():
    print(listing.name, listing.url)          # url is composite /l/{id}/{slug}
    print(listing.image_url, listing.currency)

# Need full details? Fetch by ID — returns ListingDetailResponse (includes stats)
full = client.listings.get(listing.id)
print(full.deliverable, full.reviews, full.faqs, full.stats)

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
    print("Order is in a final state (fulfilled)")

# Fulfill a paid order — push content for ListBee to deliver
if order.needs_fulfillment:
    order = client.orders.fulfill(
        order.id,
        deliverable=Deliverable.text("Your generated report..."),
    )
```

### Listing State Helpers

```python
listing = client.listings.get("lst_r7kq2xy9m3pR5tW1")

# Publication state
if listing.is_draft:
    print("Listing is not yet publishable")
if listing.is_published:
    print("Listing is live and purchasable")
if listing.is_archived:
    print("Listing has been archived")

# Deliverable state (MANAGED mode)
if listing.deliverable:
    print(f"Has deliverable: {listing.deliverable.type}")
    print(f"Content: {listing.deliverable.content}")  # url or text value

# Checkout link — composite /l/{id}/{slug}
print(f"Share: {listing.checkout_url}")

# Stats (available on GET/PUT responses)
print(f"Views: {listing.stats.views}")
print(f"Purchases: {listing.stats.purchases}")

# Readiness — use buyable
if not listing.readiness.buyable:
    print(f"Not buyable: {listing.readiness.next}")
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
listing = client.listings.get("lst_r7kq2xy9m3pR5tW1")
if not listing.readiness.is_ready:   # is_ready checks buyable
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
secret = "whsec_..."    # listing signing secret

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
    for err in e.errors:   # per-field validation errors (list of FieldValidationError)
        print(f"  {err.loc}: {err.msg}")
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
| `errors` | `list[FieldValidationError]` | Per-field validation errors (422 only) |

`RateLimitError` additionally exposes `limit`, `remaining`, and `reset` (parsed from response headers).

Each `FieldValidationError` in `errors` has `loc` (list of path segments), `msg` (human-readable), and `type` (Pydantic error code).

## Async Usage

Use `AsyncListBee` for async frameworks (FastAPI, aiohttp, etc.):

```python
import asyncio
from listbee import AsyncListBee, Deliverable

async def main():
    client = AsyncListBee(api_key="lb_...")

    # Create a listing and publish
    result = await client.listings.create(
        name="SEO Playbook",
        price=2900,
        deliverable=Deliverable.url("https://example.com/seo-playbook.pdf"),
    )
    # result is a ListingCreateResponse envelope
    print(result.signing_secret)   # store immediately!
    listing = await client.listings.publish(result.listing.id)
    print(listing.url)

    # Iterate all listings
    async for listing in await client.listings.list():
        print(listing.image_url, listing.name)

    # Filter paid orders
    async for order in await client.orders.list(status="paid"):
        print(order.id)

    # Fulfill an async-mode order — push generated content
    order = await client.orders.fulfill(
        "ord_9xM4kP7nR2qT5wY1",
        deliverable=Deliverable.text("Generated content here"),
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
    ListingResponse,         # full listing (returned by get())
    ListingSummary,          # slim listing (returned by list())
    OrderResponse,           # full order (returned by get())
    OrderSummary,            # slim order (returned by list())
    AccountResponse,
    BootstrapStartResponse,
    BootstrapVerifyResponse,
    BootstrapPollResponse,
    ApiKeyResponse,
    EventResponse,
    DeliverableResponse,
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
    Deliverable,         # input class: .url() | .text()

    # Enums
    ActionPriority,      # "required" | "suggested"
    DeliverableType,     # "url" | "text"
    FulfillmentMode,     # "static" | "async"
    PaymentStatus,       # "unpaid" | "paid" | "refunded"
    CheckoutFieldType,   # "text" | "select" | "date"
    BlurMode,            # "auto" | "true" | "false"
    ListingStatus,       # "draft" | "published" | "archived"
    OrderStatus,         # "paid" | "fulfilled"
    WebhookEventType,    # "order.paid" | "order.fulfilled" | "order.refunded" | ...
    ActionCode,          # "stripe_connect_required" | "listing_deliverable_missing" | ...
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
from listbee import ActionPriority, DeliverableType, FulfillmentMode, ActionCode, ActionKind, WebhookEventType

# Check fulfillment mode
if listing.fulfillment_mode == FulfillmentMode.STATIC:
    print(f"Delivers: {listing.deliverable.type if listing.deliverable else 'none'}")

# Check for required actions on an order
if order.actions:
    required = [a for a in order.actions if a.priority == ActionPriority.REQUIRED]
    for action in required:
        print(f"Required: {action.code} — {action.message}")

# Branch on action code
for action in listing.readiness.actions:
    if action.code == ActionCode.LISTING_DELIVERABLE_MISSING:
        print(f"Attach a deliverable: {action.resolve.endpoint}")
    elif action.code == ActionCode.STRIPE_CONNECT_REQUIRED:
        print(f"Connect Stripe: {action.resolve.url}")
```

## Migration Guide

### From v0.19.x to v0.22.0

**Breaking Change: Bootstrap flow changed — now 2-step (start → verify)**

```python
# Old (v0.19.x — 3-step flow)
session = client.bootstrap.start(email="seller@example.com")
verified = client.bootstrap.verify(session=session.session, code="123456")
result = client.bootstrap.complete(session=verified.session)
print(result.api_key)

# New (v0.22.0 — 2-step: start → verify returns api_key directly)
session = client.bootstrap.start(email="seller@example.com")
result = client.bootstrap.verify(
    bootstrap_token=session.bootstrap_token,
    otp_code="123456",
)
print(result.api_key)   # lb_... — returned immediately, store securely
```

**Breaking Change: Fulfillment model — `fulfillment_url` replaced by `fulfillment_mode` + `agent_callback_url`**

```python
# Old (v0.19.x)
listing = client.listings.create(
    name="Custom Report",
    price=4900,
    fulfillment_url="https://yourapp.com/webhooks/listbee/fulfill",
)

# New (v0.22.0)
listing = client.listings.create(
    name="Custom Report",
    price=4900,
    fulfillment_mode="async",
    agent_callback_url="https://yourapp.com/webhooks/listbee",
)
```

**Breaking Change: Single deliverable — `deliverables` (list) replaced by `deliverable` (single object)**

```python
# Old (v0.19.x)
listing = client.listings.create_complete(
    name="SEO Playbook",
    price=2900,
    deliverables=[Deliverable.url("https://example.com/seo-playbook.pdf")],
)

# New (v0.22.0)
listing = client.listings.create(
    name="SEO Playbook",
    price=2900,
    fulfillment_mode="static",
    deliverable=Deliverable.url("https://example.com/seo-playbook.pdf"),
)
```

**Breaking Change: `orders.fulfill()` now takes `deliverable=` (single) not `deliverables=` (list)**

```python
# Old (v0.19.x)
order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverables=[Deliverable.text("Your report...")],
)

# New (v0.22.0)
order = client.orders.fulfill(
    "ord_9xM4kP7nR2qT5wY1",
    deliverable=Deliverable.text("Your report..."),
)
```

**Breaking Change: ActionCode values changed**

```python
# Old (v0.19.x) → New (v0.22.0)
# ActionCode.CONNECT_STRIPE       → ActionCode.STRIPE_CONNECT_REQUIRED
# ActionCode.ATTACH_DELIVERABLE   → ActionCode.LISTING_DELIVERABLE_MISSING
# ActionCode.CONFIGURE_WEBHOOK    → ActionCode.FULFILLMENT_PENDING
# ActionCode.PUBLISH_LISTING      → ActionCode.LISTING_UNPUBLISHED
```

**Breaking Change: OrderStatus simplified**

`PENDING`, `CANCELED`, `FAILED` removed. Lifecycle is now `PAID → FULFILLED`.

**Removed: Webhooks, Customers, Files resources**

`client.webhooks`, `client.customers`, and `client.files` no longer exist. Deliverable access is handled via listing-level `agent_callback_url` and order events.

**New: Events and ApiKeys resources**

```python
# List events
for event in client.events.list():
    print(event.type, event.data)

# Self-revoke the current API key
client.api_keys.self_revoke()
```

**New: `listings.unpublish()` and `listings.archive()`**

```python
listing = client.listings.unpublish("lst_abc123")   # draft again
listing = client.listings.archive("lst_abc123")     # permanently archived
```

### From v0.15.x to v0.19.x

**Breaking Change: Store resource removed**

`client.store` no longer exists. `StoreResponse` and `StoreReadiness` types are removed.

**Breaking Change: Listing `slug` field replaced by `short_code`**

```python
# Old
print(listing.slug)        # "seo-playbook"

# New
print(listing.short_code)  # "r7kq2xy" — 7-char base62 code
```

### From v0.14.x to v0.15.x

**Breaking Change: Content Type → Implicit Fulfillment Model**

The `content_type` field was removed. Fulfillment was determined implicitly by whether deliverables were attached or a `fulfillment_url` was set.

**Changed: OrderStatus**

`PROCESSING` and `HANDED_OFF` removed. Lifecycle was `PENDING → PAID → FULFILLED`.

### From v0.13.x to v0.14.0

**Breaking Change: Fulfillment → Content Type**

The fulfillment concept was replaced with content types in v0.14.0. See v0.14.0 release notes for details.

### From v0.12.x to v0.13.x

**Breaking Change: Removed signup resource**

Account creation moved to the ListBee Console. The `client.signup` resource was removed.

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
