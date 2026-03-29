"""Listings resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee._constants import LISTING_CREATE_TIMEOUT
from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee.types.listing import ListingResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Listings:
    """Sync resource for the /v1/listings endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(
        self,
        *,
        name: str,
        price: int,
        currency: str,
        content: str,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        cover_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        cover_blur: str = "auto",
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
        timeout: float | None = None,
    ) -> ListingResponse:
        """Create a new listing.

        Builds the request body from non-None params. ``cover_blur`` is only
        included when it differs from the API default of ``"auto"``.

        Args:
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            currency: Three-letter ISO currency code, uppercase (e.g. "USD").
            content: File URL, redirect URL, or plain text to deliver after purchase.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text. Defaults to "Buy Now" when not set.
            cover_url: URL of a cover image to fetch and store.
            metadata: Arbitrary key-value pairs forwarded in webhook events.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            cover_blur: Cover blur mode — "auto", "true", or "false". Only sent
                when different from "auto".
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.
            timeout: Request timeout in seconds. Defaults to
                ``LISTING_CREATE_TIMEOUT`` (120s) because cover processing can
                take a while.

        Returns:
            The created :class:`~listbee.types.listing.ListingResponse`.
        """
        body: dict[str, Any] = {
            "name": name,
            "price": price,
            "currency": currency,
            "content": content,
        }
        if description is not None:
            body["description"] = description
        if tagline is not None:
            body["tagline"] = tagline
        if highlights is not None:
            body["highlights"] = highlights
        if cta is not None:
            body["cta"] = cta
        if cover_url is not None:
            body["cover_url"] = cover_url
        if metadata is not None:
            body["metadata"] = metadata
        if compare_at_price is not None:
            body["compare_at_price"] = compare_at_price
        if badges is not None:
            body["badges"] = badges
        if cover_blur != "auto":
            body["cover_blur"] = cover_blur
        if rating is not None:
            body["rating"] = rating
        if rating_count is not None:
            body["rating_count"] = rating_count
        if reviews is not None:
            body["reviews"] = reviews
        if faqs is not None:
            body["faqs"] = faqs

        effective_timeout = timeout if timeout is not None else LISTING_CREATE_TIMEOUT
        response = self._client.post("/v1/listings", json=body, timeout=effective_timeout)
        return ListingResponse.model_validate(response.json())

    def get(self, slug: str) -> ListingResponse:
        """Retrieve a listing by its URL slug.

        Args:
            slug: The listing's URL slug (e.g. "seo-playbook").

        Returns:
            The :class:`~listbee.types.listing.ListingResponse` for that slug.
        """
        response = self._client.get(f"/v1/listings/{slug}")
        return ListingResponse.model_validate(response.json())

    def list(self, *, limit: int = 20, cursor: str | None = None) -> SyncCursorPage[ListingResponse]:
        """Return a paginated list of listings.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for listing in client.listings.list():
                print(listing.name)

        Args:
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.listing.ListingResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        return self._client.get_page("/v1/listings", params, ListingResponse)

    def delete(self, slug: str) -> None:
        """Delete a listing.

        Args:
            slug: The listing's URL slug (e.g. "seo-playbook").
        """
        self._client.delete(f"/v1/listings/{slug}")


class AsyncListings:
    """Async resource for the /v1/listings endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        name: str,
        price: int,
        currency: str,
        content: str,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        cover_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        cover_blur: str = "auto",
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
        timeout: float | None = None,
    ) -> ListingResponse:
        """Create a new listing (async).

        Builds the request body from non-None params. ``cover_blur`` is only
        included when it differs from the API default of ``"auto"``.

        Args:
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            currency: Three-letter ISO currency code, uppercase (e.g. "USD").
            content: File URL, redirect URL, or plain text to deliver after purchase.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text. Defaults to "Buy Now" when not set.
            cover_url: URL of a cover image to fetch and store.
            metadata: Arbitrary key-value pairs forwarded in webhook events.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            cover_blur: Cover blur mode — "auto", "true", or "false". Only sent
                when different from "auto".
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.
            timeout: Request timeout in seconds. Defaults to
                ``LISTING_CREATE_TIMEOUT`` (120s) because cover processing can
                take a while.

        Returns:
            The created :class:`~listbee.types.listing.ListingResponse`.
        """
        body: dict[str, Any] = {
            "name": name,
            "price": price,
            "currency": currency,
            "content": content,
        }
        if description is not None:
            body["description"] = description
        if tagline is not None:
            body["tagline"] = tagline
        if highlights is not None:
            body["highlights"] = highlights
        if cta is not None:
            body["cta"] = cta
        if cover_url is not None:
            body["cover_url"] = cover_url
        if metadata is not None:
            body["metadata"] = metadata
        if compare_at_price is not None:
            body["compare_at_price"] = compare_at_price
        if badges is not None:
            body["badges"] = badges
        if cover_blur != "auto":
            body["cover_blur"] = cover_blur
        if rating is not None:
            body["rating"] = rating
        if rating_count is not None:
            body["rating_count"] = rating_count
        if reviews is not None:
            body["reviews"] = reviews
        if faqs is not None:
            body["faqs"] = faqs

        effective_timeout = timeout if timeout is not None else LISTING_CREATE_TIMEOUT
        response = await self._client.post("/v1/listings", json=body, timeout=effective_timeout)
        return ListingResponse.model_validate(response.json())

    async def get(self, slug: str) -> ListingResponse:
        """Retrieve a listing by its URL slug (async).

        Args:
            slug: The listing's URL slug (e.g. "seo-playbook").

        Returns:
            The :class:`~listbee.types.listing.ListingResponse` for that slug.
        """
        response = await self._client.get(f"/v1/listings/{slug}")
        return ListingResponse.model_validate(response.json())

    async def list(self, *, limit: int = 20, cursor: str | None = None) -> AsyncCursorPage[ListingResponse]:
        """Return a paginated list of listings (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for listing in await client.listings.list():
                print(listing.name)

        Args:
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.listing.ListingResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        return await self._client.get_page("/v1/listings", params, ListingResponse)

    async def delete(self, slug: str) -> None:
        """Delete a listing (async).

        Args:
            slug: The listing's URL slug (e.g. "seo-playbook").
        """
        await self._client.delete(f"/v1/listings/{slug}")
