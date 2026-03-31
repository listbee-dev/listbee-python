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
