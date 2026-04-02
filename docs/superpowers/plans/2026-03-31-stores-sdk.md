# Stores SDK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `client.stores` resource to the Python SDK covering all Store CRUD, Stripe Connect, and custom domain endpoints, plus `store_id` on listing create.

**Architecture:** New `Stores` / `AsyncStores` resource classes following existing patterns (sync + async classes in one file). New `Store`, `StoreList`, `Domain`, `DomainStatus` types. Wire into `_client.py`. The `StripeConnectSessionResponse` type already exists and is reused.

**Tech Stack:** Python 3.10+, httpx, Pydantic v2, respx (tests), ruff (lint)

**Test command:** `cd /Users/damjan/development/listbee-dev/listbee-python && uv run pytest -x -v 2>&1`

**Lint command:** `cd /Users/damjan/development/listbee-dev/listbee-python && uv run ruff check src/ tests/ 2>&1`

---

### Task 1: Store types

**Files:**
- Create: `src/listbee/types/store.py`
- Modify: `src/listbee/types/shared.py` (add `DomainStatus` enum)
- Modify: `src/listbee/types/__init__.py` (export new types)
- Modify: `src/listbee/__init__.py` (export new types)

- [ ] **Step 1: Add `DomainStatus` enum to shared.py**

In `src/listbee/types/shared.py`, add after the `ListingStatus` class:

```python
class DomainStatus(StrEnum):
    """Verification status of a custom domain."""

    PENDING = "pending"
    VERIFIED = "verified"
    STALE = "stale"
```

- [ ] **Step 2: Create `src/listbee/types/store.py`**

```python
"""Store and domain response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from listbee.types.shared import DomainStatus


class StoreResponse(BaseModel):
    """Store object returned by the ListBee API."""

    model_config = ConfigDict(frozen=True)

    object: Literal["store"] = Field(
        default="store",
        description="Object type discriminator. Always `store`.",
        examples=["store"],
    )
    id: str = Field(
        description="Unique store identifier.",
        examples=["str_7kQ2xY9mN3pR5tW1vB8a"],
    )
    handle: str = Field(
        description="URL-safe handle used in platform URLs.",
        examples=["fitness-brand"],
    )
    name: str | None = Field(
        default=None,
        description="Store display name. Falls back to @handle if not set.",
        examples=["Fitness Brand"],
    )
    display_name: str = Field(
        description="Resolved display name: name if set, otherwise @handle.",
        examples=["Fitness Brand"],
    )
    bio: str | None = Field(
        default=None,
        description="Short store bio.",
        examples=["We sell great stuff"],
    )
    social_links: list[str] = Field(
        default_factory=list,
        description="Social media URLs.",
    )
    payment_connected: bool = Field(
        description="True when the store has a payment provider configured and ready to accept payments.",
        examples=[True],
    )
    payment_provider: str | None = Field(
        default=None,
        description="Payment provider name: 'stripe', 'manual', or 'whop'. Null if not configured.",
        examples=["stripe"],
    )
    currency: str | None = Field(
        default=None,
        description="Default currency code (ISO 4217, lowercase). Null until payment is configured.",
        examples=["usd"],
    )
    domain: str | None = Field(
        default=None,
        description="Custom domain configured on this store. Null if not set.",
        examples=["fitness.com"],
    )
    domain_status: DomainStatus | None = Field(
        default=None,
        description="Domain verification status. Null if no domain configured.",
        examples=["verified"],
    )
    listing_count: int = Field(
        default=0,
        description="Number of listings in this store.",
        examples=[5],
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the store was created.",
    )


class StoreListResponse(BaseModel):
    """Non-paginated list of stores."""

    model_config = ConfigDict(frozen=True)

    object: Literal["list"] = Field(
        default="list",
        description="Object type discriminator. Always `list`.",
        examples=["list"],
    )
    data: list[StoreResponse] = Field(
        description="Array of store objects.",
    )


class DomainResponse(BaseModel):
    """Custom domain object returned by the ListBee API."""

    model_config = ConfigDict(frozen=True)

    object: Literal["domain"] = Field(
        default="domain",
        description="Object type discriminator. Always `domain`.",
        examples=["domain"],
    )
    domain: str = Field(
        description="The custom domain.",
        examples=["fitness.com"],
    )
    status: DomainStatus = Field(
        description="Verification status: pending, verified, or stale.",
        examples=["verified"],
    )
    cname_target: str = Field(
        description="The CNAME target the domain must point to.",
        examples=["buy.listbee.so"],
    )
    verified_at: datetime | None = Field(
        default=None,
        description="Timestamp when domain was verified. Null if not yet verified.",
    )
```

- [ ] **Step 3: Export from `types/__init__.py`**

Add imports and `__all__` entries:

```python
from listbee.types.store import DomainResponse, StoreListResponse, StoreResponse
```

Add to `__all__`:
```python
    # Store
    "StoreResponse",
    "StoreListResponse",
    "DomainResponse",
```

Also add the `DomainStatus` import from shared and to `__all__`:
```python
    "DomainStatus",
```

- [ ] **Step 4: Export from top-level `__init__.py`**

Add to the `from listbee.types import (...)` block:
```python
    DomainResponse,
    DomainStatus,
    StoreListResponse,
    StoreResponse,
```

Add to `__all__`:
```python
    "DomainResponse",
    "DomainStatus",
    "StoreListResponse",
    "StoreResponse",
```

- [ ] **Step 5: Run lint**

Run: `cd /Users/damjan/development/listbee-dev/listbee-python && uv run ruff check src/ 2>&1`
Expected: PASS (no errors)

- [ ] **Step 6: Commit**

```bash
git add src/listbee/types/store.py src/listbee/types/shared.py src/listbee/types/__init__.py src/listbee/__init__.py
git commit -m "feat: add Store, StoreList, Domain, DomainStatus types"
```

---

### Task 2: Stores resource

**Files:**
- Create: `src/listbee/resources/stores.py`
- Modify: `src/listbee/resources/__init__.py` (export)
- Modify: `src/listbee/_client.py` (wire `self.stores`)

- [ ] **Step 1: Create `src/listbee/resources/stores.py`**

```python
"""Stores resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee.types.store import DomainResponse, StoreListResponse, StoreResponse
from listbee.types.stripe import StripeConnectSessionResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Stores:
    """Sync resource for the /v1/stores endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(self, *, handle: str, name: str | None = None) -> StoreResponse:
        """Create a new store.

        Args:
            handle: URL-safe handle, unique globally. Used in platform URLs:
                ``buy.listbee.so/@{handle}/{slug}``.
            name: Optional display name. Falls back to @handle if not set.

        Returns:
            The created :class:`~listbee.types.store.StoreResponse`.
        """
        body: dict[str, Any] = {"handle": handle}
        if name is not None:
            body["name"] = name
        response = self._client.post("/v1/stores", json=body)
        return StoreResponse.model_validate(response.json())

    def list(self) -> StoreListResponse:
        """List all stores for the authenticated account.

        Returns:
            A :class:`~listbee.types.store.StoreListResponse` containing all stores.
        """
        response = self._client.get("/v1/stores")
        return StoreListResponse.model_validate(response.json())

    def get(self, store_id: str) -> StoreResponse:
        """Retrieve a store by ID.

        Args:
            store_id: The store ID (e.g. ``"str_7kQ2xY9mN3pR5tW1vB8a"``).

        Returns:
            The :class:`~listbee.types.store.StoreResponse`.
        """
        response = self._client.get(f"/v1/stores/{store_id}")
        return StoreResponse.model_validate(response.json())

    def update(
        self,
        store_id: str,
        *,
        name: str | None = None,
        bio: str | None = None,
        social_links: list[str] | None = None,
    ) -> StoreResponse:
        """Update a store.

        Only the supplied fields are updated; all others remain unchanged.

        Args:
            store_id: The store ID.
            name: Store display name.
            bio: Short store bio.
            social_links: Social media URLs (HTTPS only, max 5).

        Returns:
            The updated :class:`~listbee.types.store.StoreResponse`.
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if bio is not None:
            body["bio"] = bio
        if social_links is not None:
            body["social_links"] = social_links
        response = self._client.patch(f"/v1/stores/{store_id}", json=body)
        return StoreResponse.model_validate(response.json())

    def delete(self, store_id: str) -> None:
        """Delete a store.

        Args:
            store_id: The store ID.
        """
        self._client.delete(f"/v1/stores/{store_id}")

    def connect_stripe(self, store_id: str) -> StripeConnectSessionResponse:
        """Start Stripe Connect onboarding for a store.

        Args:
            store_id: The store ID.

        Returns:
            A :class:`~listbee.types.stripe.StripeConnectSessionResponse` with
            a URL to redirect the user to Stripe's onboarding flow.
        """
        response = self._client.post(f"/v1/stores/{store_id}/stripe/connect")
        return StripeConnectSessionResponse.model_validate(response.json())

    def set_domain(self, store_id: str, *, domain: str) -> DomainResponse:
        """Set a custom domain on a store.

        The domain's CNAME must point to ``buy.listbee.so`` for verification.

        Args:
            store_id: The store ID.
            domain: Custom domain hostname (no protocol, no path).

        Returns:
            The :class:`~listbee.types.store.DomainResponse` with verification status.
        """
        response = self._client.put(f"/v1/stores/{store_id}/domain", json={"domain": domain})
        return DomainResponse.model_validate(response.json())

    def verify_domain(self, store_id: str) -> DomainResponse:
        """Verify a store's custom domain DNS configuration.

        Args:
            store_id: The store ID.

        Returns:
            The :class:`~listbee.types.store.DomainResponse` with updated status.
        """
        response = self._client.post(f"/v1/stores/{store_id}/domain/verify")
        return DomainResponse.model_validate(response.json())

    def remove_domain(self, store_id: str) -> None:
        """Remove a store's custom domain.

        Args:
            store_id: The store ID.
        """
        self._client.delete(f"/v1/stores/{store_id}/domain")


class AsyncStores:
    """Async resource for the /v1/stores endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, *, handle: str, name: str | None = None) -> StoreResponse:
        """Create a new store (async).

        Args:
            handle: URL-safe handle, unique globally. Used in platform URLs:
                ``buy.listbee.so/@{handle}/{slug}``.
            name: Optional display name. Falls back to @handle if not set.

        Returns:
            The created :class:`~listbee.types.store.StoreResponse`.
        """
        body: dict[str, Any] = {"handle": handle}
        if name is not None:
            body["name"] = name
        response = await self._client.post("/v1/stores", json=body)
        return StoreResponse.model_validate(response.json())

    async def list(self) -> StoreListResponse:
        """List all stores for the authenticated account (async).

        Returns:
            A :class:`~listbee.types.store.StoreListResponse` containing all stores.
        """
        response = await self._client.get("/v1/stores")
        return StoreListResponse.model_validate(response.json())

    async def get(self, store_id: str) -> StoreResponse:
        """Retrieve a store by ID (async).

        Args:
            store_id: The store ID (e.g. ``"str_7kQ2xY9mN3pR5tW1vB8a"``).

        Returns:
            The :class:`~listbee.types.store.StoreResponse`.
        """
        response = await self._client.get(f"/v1/stores/{store_id}")
        return StoreResponse.model_validate(response.json())

    async def update(
        self,
        store_id: str,
        *,
        name: str | None = None,
        bio: str | None = None,
        social_links: list[str] | None = None,
    ) -> StoreResponse:
        """Update a store (async).

        Only the supplied fields are updated; all others remain unchanged.

        Args:
            store_id: The store ID.
            name: Store display name.
            bio: Short store bio.
            social_links: Social media URLs (HTTPS only, max 5).

        Returns:
            The updated :class:`~listbee.types.store.StoreResponse`.
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if bio is not None:
            body["bio"] = bio
        if social_links is not None:
            body["social_links"] = social_links
        response = await self._client.patch(f"/v1/stores/{store_id}", json=body)
        return StoreResponse.model_validate(response.json())

    async def delete(self, store_id: str) -> None:
        """Delete a store (async).

        Args:
            store_id: The store ID.
        """
        await self._client.delete(f"/v1/stores/{store_id}")

    async def connect_stripe(self, store_id: str) -> StripeConnectSessionResponse:
        """Start Stripe Connect onboarding for a store (async).

        Args:
            store_id: The store ID.

        Returns:
            A :class:`~listbee.types.stripe.StripeConnectSessionResponse` with
            a URL to redirect the user to Stripe's onboarding flow.
        """
        response = await self._client.post(f"/v1/stores/{store_id}/stripe/connect")
        return StripeConnectSessionResponse.model_validate(response.json())

    async def set_domain(self, store_id: str, *, domain: str) -> DomainResponse:
        """Set a custom domain on a store (async).

        The domain's CNAME must point to ``buy.listbee.so`` for verification.

        Args:
            store_id: The store ID.
            domain: Custom domain hostname (no protocol, no path).

        Returns:
            The :class:`~listbee.types.store.DomainResponse` with verification status.
        """
        response = await self._client.put(f"/v1/stores/{store_id}/domain", json={"domain": domain})
        return DomainResponse.model_validate(response.json())

    async def verify_domain(self, store_id: str) -> DomainResponse:
        """Verify a store's custom domain DNS configuration (async).

        Args:
            store_id: The store ID.

        Returns:
            The :class:`~listbee.types.store.DomainResponse` with updated status.
        """
        response = await self._client.post(f"/v1/stores/{store_id}/domain/verify")
        return DomainResponse.model_validate(response.json())

    async def remove_domain(self, store_id: str) -> None:
        """Remove a store's custom domain (async).

        Args:
            store_id: The store ID.
        """
        await self._client.delete(f"/v1/stores/{store_id}/domain")
```

- [ ] **Step 2: Check if `_base_client.py` has a `patch` method**

The API uses `PATCH /v1/stores/{id}` for updates. Check if `SyncClient` and `AsyncClient` have `patch()`. If not, add them following the same pattern as `put()`.

Run: `grep -n "def patch" src/listbee/_base_client.py`

If missing, add to `SyncClient` (after the `put` method):
```python
    def patch(
        self, path: str, *, json: dict[str, Any] | None = None, timeout: float | None = None
    ) -> httpx.Response:
        """Send a PATCH request."""
        return self._request("PATCH", path, json=json, timeout=timeout)
```

And to `AsyncClient` (after its `put` method):
```python
    async def patch(
        self, path: str, *, json: dict[str, Any] | None = None, timeout: float | None = None
    ) -> httpx.Response:
        """Send a PATCH request."""
        return await self._request("PATCH", path, json=json, timeout=timeout)
```

- [ ] **Step 3: Export from `resources/__init__.py`**

Add:
```python
from listbee.resources.stores import AsyncStores, Stores
```

Add to `__all__`:
```python
    "AsyncStores",
    "Stores",
```

- [ ] **Step 4: Wire in `_client.py`**

Add import:
```python
from listbee.resources.stores import AsyncStores, Stores
```

Add to `ListBee.__init__`:
```python
        self.stores = Stores(self)
```

Add to `AsyncListBee.__init__`:
```python
        self.stores = AsyncStores(self)
```

- [ ] **Step 5: Run lint**

Run: `cd /Users/damjan/development/listbee-dev/listbee-python && uv run ruff check src/ 2>&1`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/listbee/resources/stores.py src/listbee/resources/__init__.py src/listbee/_client.py src/listbee/_base_client.py
git commit -m "feat: add Stores resource with CRUD, Stripe Connect, and domain methods"
```

---

### Task 3: Store tests

**Files:**
- Create: `tests/test_stores.py`

- [ ] **Step 1: Create `tests/test_stores.py`**

```python
"""Tests for the Stores resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.stores import Stores
from listbee.types.store import DomainResponse, StoreListResponse, StoreResponse
from listbee.types.stripe import StripeConnectSessionResponse

STORE_JSON = {
    "object": "store",
    "id": "str_7kQ2xY9mN3pR5tW1vB8a",
    "handle": "fitness-brand",
    "name": "Fitness Brand",
    "display_name": "Fitness Brand",
    "bio": None,
    "social_links": [],
    "payment_connected": False,
    "payment_provider": None,
    "currency": None,
    "domain": None,
    "domain_status": None,
    "listing_count": 0,
    "created_at": "2026-03-31T12:00:00Z",
}

STORE_LIST_JSON = {
    "object": "list",
    "data": [STORE_JSON],
}

DOMAIN_JSON = {
    "object": "domain",
    "domain": "fitness.com",
    "status": "pending",
    "cname_target": "buy.listbee.so",
    "verified_at": None,
}

CONNECT_SESSION_JSON = {
    "object": "stripe_connect_session",
    "url": "https://connect.stripe.com/setup/s/abc123",
    "expires_at": "2026-03-31T13:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def stores(sync_client):
    return Stores(sync_client)


class TestCreateStore:
    def test_create_returns_store_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_JSON))
            result = stores.create(handle="fitness-brand")
        assert isinstance(result, StoreResponse)
        assert result.id == "str_7kQ2xY9mN3pR5tW1vB8a"
        assert result.handle == "fitness-brand"
        assert result.object == "store"

    def test_create_sends_correct_body(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_JSON))
            stores.create(handle="fitness-brand", name="Fitness Brand")
        body = json.loads(route.calls[0].request.content)
        assert body == {"handle": "fitness-brand", "name": "Fitness Brand"}

    def test_create_omits_name_when_none(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_JSON))
            stores.create(handle="fitness-brand")
        body = json.loads(route.calls[0].request.content)
        assert body == {"handle": "fitness-brand"}


class TestListStores:
    def test_list_returns_store_list_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/stores").mock(return_value=httpx.Response(200, json=STORE_LIST_JSON))
            result = stores.list()
        assert isinstance(result, StoreListResponse)
        assert len(result.data) == 1
        assert result.data[0].handle == "fitness-brand"


class TestGetStore:
    def test_get_returns_store_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(
                return_value=httpx.Response(200, json=STORE_JSON)
            )
            result = stores.get("str_7kQ2xY9mN3pR5tW1vB8a")
        assert isinstance(result, StoreResponse)
        assert result.id == "str_7kQ2xY9mN3pR5tW1vB8a"


class TestUpdateStore:
    def test_update_returns_store_response(self, stores):
        updated = {**STORE_JSON, "name": "New Name", "bio": "Great stuff"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.patch("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(
                return_value=httpx.Response(200, json=updated)
            )
            result = stores.update("str_7kQ2xY9mN3pR5tW1vB8a", name="New Name", bio="Great stuff")
        assert isinstance(result, StoreResponse)
        assert result.name == "New Name"

    def test_update_sends_only_provided_fields(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.patch("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(
                return_value=httpx.Response(200, json=STORE_JSON)
            )
            stores.update("str_7kQ2xY9mN3pR5tW1vB8a", name="New Name")
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "New Name"}
        assert "bio" not in body
        assert "social_links" not in body


class TestDeleteStore:
    def test_delete_sends_request(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a").mock(
                return_value=httpx.Response(204)
            )
            result = stores.delete("str_7kQ2xY9mN3pR5tW1vB8a")
        assert result is None


class TestConnectStripe:
    def test_connect_stripe_returns_session(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/stripe/connect").mock(
                return_value=httpx.Response(200, json=CONNECT_SESSION_JSON)
            )
            result = stores.connect_stripe("str_7kQ2xY9mN3pR5tW1vB8a")
        assert isinstance(result, StripeConnectSessionResponse)
        assert result.url == "https://connect.stripe.com/setup/s/abc123"


class TestSetDomain:
    def test_set_domain_returns_domain_response(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain").mock(
                return_value=httpx.Response(200, json=DOMAIN_JSON)
            )
            result = stores.set_domain("str_7kQ2xY9mN3pR5tW1vB8a", domain="fitness.com")
        assert isinstance(result, DomainResponse)
        assert result.domain == "fitness.com"
        assert result.status == "pending"
        assert result.cname_target == "buy.listbee.so"

    def test_set_domain_sends_correct_body(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain").mock(
                return_value=httpx.Response(200, json=DOMAIN_JSON)
            )
            stores.set_domain("str_7kQ2xY9mN3pR5tW1vB8a", domain="fitness.com")
        body = json.loads(route.calls[0].request.content)
        assert body == {"domain": "fitness.com"}


class TestVerifyDomain:
    def test_verify_domain_returns_domain_response(self, stores):
        verified = {**DOMAIN_JSON, "status": "verified", "verified_at": "2026-03-31T13:00:00Z"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain/verify").mock(
                return_value=httpx.Response(200, json=verified)
            )
            result = stores.verify_domain("str_7kQ2xY9mN3pR5tW1vB8a")
        assert isinstance(result, DomainResponse)
        assert result.status == "verified"
        assert result.verified_at is not None


class TestRemoveDomain:
    def test_remove_domain_sends_request(self, stores):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/stores/str_7kQ2xY9mN3pR5tW1vB8a/domain").mock(
                return_value=httpx.Response(204)
            )
            result = stores.remove_domain("str_7kQ2xY9mN3pR5tW1vB8a")
        assert result is None
```

- [ ] **Step 2: Run tests**

Run: `cd /Users/damjan/development/listbee-dev/listbee-python && uv run pytest tests/test_stores.py -x -v 2>&1`
Expected: All 13 tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_stores.py
git commit -m "test: add stores resource tests"
```

---

### Task 4: Add `store_id` to listing create

**Files:**
- Modify: `src/listbee/resources/listings.py` (add `store_id` param to `create` in both Listings and AsyncListings)
- Modify: `tests/test_listings.py` (add test for `store_id`)

- [ ] **Step 1: Add `store_id` parameter to `Listings.create()`**

In `src/listbee/resources/listings.py`, add `store_id: str | None = None` as the first keyword-only parameter of `Listings.create()`, right after `self` and before `name`:

```python
    def create(
        self,
        *,
        name: str,
        price: int,
        content: str,
        store_id: str | None = None,
        description: str | None = None,
        # ... rest of params unchanged
```

Add to the docstring Args:
```
            store_id: Store to create this listing in. Required when the account
                has multiple stores. Omit for single-store accounts.
```

Add to the body-building section (before the existing `if description` line):
```python
        if store_id is not None:
            body["store_id"] = store_id
```

Apply the same change to `AsyncListings.create()`.

- [ ] **Step 2: Add test to `tests/test_listings.py`**

Add this test method to the `TestCreateListing` class:

```python
    def test_create_listing_with_store_id(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="SEO Playbook",
                price=2999,
                content="https://example.com/file.pdf",
                store_id="str_7kQ2xY9mN3pR5tW1vB8a",
            )
        body = json.loads(route.calls[0].request.content)
        assert body["store_id"] == "str_7kQ2xY9mN3pR5tW1vB8a"
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/damjan/development/listbee-dev/listbee-python && uv run pytest tests/test_listings.py -x -v 2>&1`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/listbee/resources/listings.py tests/test_listings.py
git commit -m "feat: add store_id parameter to listings.create()"
```

---

### Task 5: Version bump, CHANGELOG, README

**Files:**
- Modify: `pyproject.toml` (bump version 0.4.0 → 0.5.0)
- Modify: `CHANGELOG.md` (add 0.5.0 section)
- Modify: `README.md` (add Stores section to usage examples)

- [ ] **Step 1: Bump version in `pyproject.toml`**

Change `version = "0.4.0"` to `version = "0.5.0"`.

- [ ] **Step 2: Update `CHANGELOG.md`**

Add above the `[Unreleased]` line:

```markdown
## [0.5.0] - 2026-03-31

### Added

- `client.stores` resource — full Store CRUD: `create()`, `list()`, `get()`, `update()`, `delete()`
- `client.stores.connect_stripe()` — start Stripe Connect onboarding for a store
- `client.stores.set_domain()`, `verify_domain()`, `remove_domain()` — custom domain management
- New types: `StoreResponse`, `StoreListResponse`, `DomainResponse`, `DomainStatus`
- `store_id` parameter on `client.listings.create()` — assign listings to specific stores
```

- [ ] **Step 3: Update README.md**

Read the current README and add a **Stores** section after the existing usage examples. Show:
- Creating a store
- Listing stores
- Connecting Stripe
- Setting a custom domain
- Creating a listing with `store_id`

- [ ] **Step 4: Run full test suite**

Run: `cd /Users/damjan/development/listbee-dev/listbee-python && uv run pytest -x -v 2>&1`
Expected: All tests PASS (existing 119 + ~14 new ≈ 133)

- [ ] **Step 5: Run lint**

Run: `cd /Users/damjan/development/listbee-dev/listbee-python && uv run ruff check src/ tests/ 2>&1`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml CHANGELOG.md README.md
git commit -m "chore: bump version to 0.5.0, update CHANGELOG and README with Stores"
```
