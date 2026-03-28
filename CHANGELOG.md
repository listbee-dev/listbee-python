# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial SDK release
- Sync (`ListBee`) and async (`AsyncListBee`) clients
- Resource methods: listings, orders, webhooks, account
- Auto-paginating cursor pages
- Typed exception hierarchy (RFC 9457)
- Automatic retries with exponential backoff on 429/5xx
- Full type annotations and inline documentation
