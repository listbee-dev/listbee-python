# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
