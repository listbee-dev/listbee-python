# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
