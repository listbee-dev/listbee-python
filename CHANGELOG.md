# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `OrderReadiness` model with `fulfilled`, `actions`, and `next` fields
- `readiness` field on `OrderResponse`
- `WebhookListResponse` type for list webhook responses

### Changed
- `PlanListResponse` now includes `cursor` and `has_more` fields (standard list envelope)
- `WebhookListResponse` now includes `cursor` and `has_more` fields (standard list envelope)
- `webhooks.list()` now accepts optional `cursor` and `limit` parameters for pagination

## [0.18.0] - 2026-04-10

### Added
- `extras` property on `APIStatusError` and all subclasses — a `dict[str, Any]` containing all RFC 9457 extension members from the error response body. Enables agents to read structured error metadata (`current_status`, `allowed_statuses`, `actions`, `retry_after`, etc.) without parsing the `detail` text.

## [0.17.0] - 2026-04-10

### Added
- `set_cover(listing_id, source)` convenience method on listings resource — accepts a `file_` token, image URL, bytes, or BinaryIO; uploads and applies in one call (sync + async)
- `set_avatar(source)` convenience method on store resource — accepts a `file_` token, image URL, bytes, or BinaryIO; uploads and applies in one call (sync + async)
- `purpose` parameter on `files.upload()` — `"deliverable"` (default), `"cover"`, or `"avatar"`
- `has_avatar` field on `StoreResponse` — `True` when a store avatar has been uploaded

### Changed
- Store `update()` parameter `avatar_url` renamed to `avatar` (file token, `file_` prefixed)

### Removed
- `avatar_url` field from `StoreResponse` (replaced by `has_avatar`)
- `avatar_url` parameter from store `update()` (replaced by `avatar`)

## [0.16.0] - 2026-04-10

### Added
- Store resource: `client.store.get()`, `client.store.update()` — brand information (display name, bio, avatar, slug) is now managed via Store
- Bootstrap resource: `client.bootstrap.start()`, `.verify()`, `.create_store()` — 3-step onboarding flow to create an account and obtain an API key without the Console

### Removed
- API Keys resource (`client.api_keys`) — replaced by the bootstrap flow; API keys are issued automatically at store creation
- `display_name`, `bio`, `has_avatar` fields from `AccountResponse` — brand info moved to `StoreResponse`
- `display_name`, `bio`, `avatar` params from `client.account.update()` — use `client.store.update()` instead

### Changed
- `AccountResponse.currency` is now lowercase ISO 4217 (e.g. `"usd"`) to match API

## [0.15.0] - 2026-04-10

### Added
- `with_raw_response` on all resources — access HTTP headers, request IDs, rate limit info without losing typed responses
- `fulfillment_url` field on `ListingResponse` and `create()`/`update()` params — set a URL to trigger external fulfillment after payment
- `has_deliverables` field on `ListingResponse` and `OrderResponse` — `true` when one or more deliverables are attached
- `actions` list on `OrderResponse` — available actions for this order, each with a `priority` field
- `ActionPriority` enum: `required` | `suggested`
- `priority` field on `Action` model

### Changed
- Remove `content_type` field from `ListingResponse` and `OrderResponse` — fulfillment behavior is now derived from `has_deliverables` and `fulfillment_url`
- Remove `handed_off_at` field from `OrderResponse`
- Remove `processing` and `handed_off` values from `OrderStatus` enum
- `create()` and `update()` on listings no longer accept `content_type` — use `fulfillment_url` to configure external fulfillment
- `needs_fulfillment` property on `OrderResponse` now checks `status == "paid"` only
- `is_terminal` property on `OrderResponse` no longer includes `handed_off` state

### Removed
- `ContentType` enum — replaced by implicit model (`has_deliverables` for managed delivery, `fulfillment_url` for external)
- `CheckoutFieldType.ADDRESS` — agents define their own fields, ListBee renders text/select/date
- `CheckoutField.address()` builder method

## [0.14.2] - 2026-04-08

### Added
- `plans.list()` method for fetching available pricing plans

## [0.14.0] - 2026-04-08

### Changed
- Replace `fulfillment` (managed/external) with `content_type` (static/generated/webhook) on `ListingResponse` — `create()` and `update()` now accept `content_type` instead of `fulfillment`
- Add `content_type`, `payment_status`, `listing_snapshot`, `seller_snapshot`, `handed_off_at` to `OrderResponse`
- Add `processing` and `handed_off` to `OrderStatus` enum
- Remove `has_deliverables` from `ListingResponse`
- Remove `shipping_address` from `OrderResponse`

### Added
- `ContentType` enum: `static` | `generated` | `webhook`
- `PaymentStatus` enum: `unpaid` | `paid` | `refunded`

### Removed
- `FulfillmentMode` enum — replaced by `ContentType`
- `ShippingAddress` type — no longer returned by the API

## [0.13.1] - 2026-04-07

### Removed
- Removed `signup` resource (`send_otp`, `verify_otp`) — account creation now handled via the ListBee Console
- Removed types: `AuthSessionResponse`, `OtpRequestResponse`

## [0.13.0] - 2026-04-07

### Changed
- Renamed `orders.deliver()` to `orders.fulfill()` with optional deliverables — call without arguments to close out an external fulfillment order, or pass `deliverables=[...]` to push content for ListBee to deliver

### Removed
- Removed `orders.ship()` — physical delivery tracking is now handled externally
- Removed shipping fields from `OrderResponse`: `carrier`, `tracking_code`, `seller_note`, `shipped_at`

### Added
- Added `notify_orders: bool` to `AccountResponse` and `account.update()` — controls email notifications for new orders

## [0.12.0] - 2026-04-07

### Added
- `CheckoutField` builder class with factory methods: `text()`, `select()`, `address()`, `date()`
- Listings resource now accepts `CheckoutField` objects alongside raw dicts for `checkout_schema`

### Changed
- Response model `CheckoutField` renamed to `CheckoutFieldResponse` (builder class takes the `CheckoutField` name)

## [0.11.1] - 2026-04-07

### Added
- `sort_order` field on `CheckoutField` for controlling display order (default: `0`, lower values shown first)

### Changed
- `CheckoutField.name` renamed to `CheckoutField.key` to match API schema

## [0.11.0] - 2026-04-07

### Changed
- Renamed `client.signup.create()` to `client.signup.send_otp()` — sends OTP to email, works for both new and existing accounts; path changed from `POST /v1/account` to `POST /v1/auth/otp`
- Renamed `client.signup.verify()` to `client.signup.verify_otp()` — path changed from `POST /v1/account/verify/otp` to `POST /v1/auth/otp/verify`; response now returns `access_token` (short-lived, 24h) instead of `api_key`, plus `is_new`, `token_type`, and `expires_in` fields

### Removed
- `CreateAccountResponse` type — replaced by `OtpRequestResponse`
- `VerifyOtpResponse` / `VerifyResponse` type — replaced by `AuthSessionResponse`
- `SignupResponse` type — replaced by `OtpRequestResponse`

### Added
- `client.utility.ping()` — authenticated connectivity check to verify API key validity (async: `client.utility.ping()`)
- `Deliverable` input class with factory methods: `.file()`, `.url()`, `.text()`, `.from_token()`
- `client.listings.add_deliverable(listing_id, deliverable)` — add a single deliverable (POST `/v1/listings/{id}/deliverables`)
- `client.listings.remove_deliverable(listing_id, deliverable_id)` — remove a single deliverable by `del_` ID
- `client.listings.create_complete()` — create a listing and attach deliverables in one call
- `PartialCreationError` — raised when listing is created but deliverable attachment fails
- `DeliverableResponse.id` — `del_` prefixed ID on all deliverable responses

### Changed
- `set_deliverables()` and `orders.deliver()` now accept `Deliverable` objects in addition to raw dicts

## [0.9.1] - 2026-04-06

### Removed
- Convenience helpers (`create_and_publish`, `upload_and_set_deliverable`, `upload_and_deliver`, `get_by_email`, `retry_failed_events`) — will be redesigned with better semantics

## [0.9.0] - 2026-04-05

### Added
- `client.listings.create_and_publish()` — create, set deliverables, and publish in one call
- `client.listings.upload_and_set_deliverable()` — upload file and attach to listing
- `client.orders.upload_and_deliver()` — upload file and deliver to order
- `client.customers.get_by_email()` — look up customer by email address
- `client.webhooks.retry_failed_events()` — retry all failed webhook events

## [0.8.0] - 2026-04-05

### Added
- `client.customers.list()` and `client.customers.get()` — buyer management
- `client.files.upload()` — file upload for deliverables (multipart)
- `client.listings.set_deliverables()` — attach deliverables to draft listings
- `client.listings.remove_deliverables()` — remove deliverables from draft listings
- `client.listings.publish()` — publish draft listings
- `client.orders.refund()` — issue full refund
- `client.webhooks.retry_event()` — retry failed webhook deliveries
- `client.account.delete()` — delete account
- Multipart upload support in base client

### Added (cont.)
- `BadRequestError` (400), `ForbiddenError` (403), `PayloadTooLargeError` (413) error types
- `AccountResponse`: `display_name`, `bio`, `has_avatar`, `billing_status` fields
- `DeliverableResponse`: `status`, `content`, `filename`, `mime_type`, `size`, `url` fields
- `WebhookResponse`: `disabled_reason`, `readiness` fields
- `WebhookEventResponse`: `failed_at`, `next_retry_at` fields
- `ListingResponse`: `stock`, `embed_url` fields
- `OrderResponse`: `refund_amount`, `refunded_at`, `dispute_amount`, `dispute_reason`, `dispute_status`, `disputed_at`, `platform_fee` fields
- `WebhookReadiness` model

### Changed
- `client.orders.fulfill()` renamed to `client.orders.deliver()` with `deliverables` list param
- `ListingResponse.deliverable` → `deliverables` (array), `has_deliverable` → `has_deliverables`
- `OrderResponse.deliverable` → `deliverables` (array)

### Fixed
- `client.signup.create()` now uses correct endpoint `POST /v1/account` (was `/v1/account/signup`)
- `client.signup.verify()` now uses correct endpoint `POST /v1/account/verify/otp` (was `/v1/account/verify`)

### Removed
- `client.stores` resource — stores removed from API
- `client.listings.pause()` and `client.listings.resume()` — replaced by draft/published flow
- `client.stripe.set_key()` — Stripe Connect is the only setup path
- `ContentType` alias — use `DeliverableType` directly
- `DomainStatus` enum — was for stores

## [0.7.0] - 2026-04-02

### Breaking

- `FulfillmentStatus` enum removed entirely — no longer returned by the API
- `OrderResponse`: `fulfillment_status` field removed; replaced by `deliverable: DeliverableResponse | None` and `shipped_at: datetime | None`
- `ListingResponse`: `deliverable_type` field removed; replaced by `deliverable: DeliverableResponse | None`
- `orders.fulfill()`: `content`, `content_type`, `content_url` params removed; replaced by `deliverable: str` (required, auto-detected by API)

### Added

- `DeliverableResponse` model: `object`, `type`, `has_content` — nested on both `ListingResponse` and `OrderResponse`
- `orders.fulfill()` now accepts a single `deliverable` string — URL, file path, or text auto-detected
- `OrderResponse.shipped_at` — ISO 8601 timestamp set when order is shipped

## [0.6.0] - 2026-04-02

### Breaking

- Renamed `ContentType` enum to `DeliverableType` (`ContentType` kept as alias for backwards compatibility)
- Listing model: `content_type` renamed to `deliverable_type`, `has_content` renamed to `has_deliverable`
- `listings.create()`: `content` parameter renamed to `deliverable`
- Order model: `stripe_session_id` field removed
- `OrderStatus` enum: `COMPLETED` replaced by `PENDING`, `PAID`, `FULFILLED`, `CANCELED`, `FAILED`
- `WebhookEventType` enum: `ORDER_COMPLETED` removed, replaced by `ORDER_PAID`, `ORDER_FULFILLED`, `ORDER_SHIPPED`

### Added

- Fulfillment architecture: two-mode system (managed + external)
- `FulfillmentMode` enum: `"managed"` | `"external"`
- `DeliverableType` enum (replaces `ContentType`): `"file"` | `"url"` | `"text"`
- `CheckoutField` and `CheckoutFieldType` models for custom checkout fields
- `ShippingAddress` model for shipping address data
- `FulfillmentStatus` enum: `"pending"` | `"shipped"` | `"fulfilled"`
- `fulfillment` and `checkout_schema` fields on `ListingResponse`
- `fulfillment` and `checkout_schema` parameters on `listings.create()` and `listings.update()`
- New order fields: `checkout_data`, `shipping_address`, `fulfillment_status`, `carrier`, `tracking_code`, `seller_note`, `paid_at`, `fulfilled_at`
- `orders.fulfill()` method — POST `/v1/orders/{id}/fulfill` for external fulfillment callback
- `orders.ship()` method — POST `/v1/orders/{id}/ship` with carrier/tracking info
- New webhook event types: `ORDER_PAID`, `ORDER_FULFILLED`, `ORDER_SHIPPED`
- `CONFIGURE_WEBHOOK` action code for external fulfillment readiness

## [0.5.0] - 2026-03-31

### Added

- `client.stores` resource — full Store CRUD: `create()`, `list()`, `get()`, `update()`, `delete()`
- `client.stores.connect_stripe()` — start Stripe Connect onboarding for a store
- `client.stores.set_domain()`, `verify_domain()`, `remove_domain()` — custom domain management
- New types: `StoreResponse`, `StoreListResponse`, `DomainResponse`, `DomainStatus`
- `store_id` parameter on `client.listings.create()` — assign listings to specific stores

## [0.3.0] - 2026-03-30

### Breaking

- Removed `currency` parameter from `listings.create()` and `listings.update()` — currency is now on the account
- Removed `currency` field from `ListingResponse`
- `ListingStatus` enum: `PUBLISHED` replaced by `ACTIVE` and `PAUSED`

### Added

- `client.listings.pause(slug)` and `client.listings.resume(slug)` — pause/resume listings (sync and async)
- `AccountStats` model with `total_revenue`, `total_orders`, `total_listings`
- `currency` and `stats` fields on `AccountResponse`
- `status` field on `ListingResponse` now supports `"active"` and `"paused"` values
- `total_count` field on all paginated list responses (`SyncCursorPage`, `AsyncCursorPage`, `CursorPage`)
- Order filtering: `listing`, `created_after`, `created_before` parameters on `orders.list()`
- New webhook event types: `listing.updated`, `listing.paused`, `listing.resumed`, `listing.deleted`

## [0.2.0] - 2026-03-30

### Breaking

- Readiness model overhauled: `Blocker`, `BlockerCode`, `BlockerAction`, `BlockerResolve` removed
- New types: `Action`, `ActionCode`, `ActionKind`, `ActionResolve`
- `ListingReadiness` and `AccountReadiness` now use `actions` list and `next` pointer instead of `blockers`

### Added

- `client.signup.create()` and `client.signup.verify()` — agent self-service onboarding (unauthenticated)
- `client.api_keys.list()`, `.create()`, `.delete()` — API key management
- `client.stripe.set_key()`, `.connect()`, `.disconnect()` — Stripe configuration
- `client.listings.update()` — partial listing updates
- Support for unauthenticated requests via `authenticated=False` parameter

## [0.1.1] - 2026-03-29

### Fixed

- Use listbee.so instead of listbee.so/console for all URLs

## [0.1.0] - 2026-03-29

### Added

- Initial SDK release
- Sync (`ListBee`) and async (`AsyncListBee`) clients
- Resource methods: listings, orders, webhooks, account
- Auto-paginating cursor pages
- Typed exception hierarchy (RFC 9457)
- Automatic retries with exponential backoff on 429/5xx
- Webhook signature verification helper
- Full type annotations and inline documentation
