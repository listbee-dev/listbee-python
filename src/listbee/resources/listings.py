"""Listings resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee._constants import LISTING_CREATE_TIMEOUT
from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee._raw_response import RawResponse
from listbee.types.listing import ListingDetailResponse, ListingSummary
from listbee.types.listing_create import ListingCreateResponse, RotateSigningSecretResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


def _resolve_checkout_schema(schema: list[Any] | None) -> list[dict[str, Any]] | None:
    """Convert CheckoutField builder objects to dicts, pass raw dicts through."""
    if schema is None:
        return None
    resolved: list[dict[str, Any]] = []
    for item in schema:
        if hasattr(item, "to_api_body"):
            resolved.append(item.to_api_body())
        else:
            resolved.append(item)
    return resolved


def _resolve_deliverable(deliverable: Any) -> dict[str, Any] | None:
    """Convert a Deliverable builder object to a dict, pass raw dicts through."""
    if deliverable is None:
        return None
    if hasattr(deliverable, "to_api_body"):
        return deliverable.to_api_body()
    return deliverable


class _RawListingsProxy:
    """Proxy that calls Listings methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(
        self,
        *,
        name: str,
        price: int,
        **kwargs: Any,
    ) -> RawResponse[ListingCreateResponse]:
        """Create a new listing and return the raw response."""
        body = {"name": name, "price": price, **{k: v for k, v in kwargs.items() if v is not None}}
        response = self._client.request_raw("POST", "/v1/listings", json=body)
        return RawResponse(response, ListingCreateResponse)

    def get(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Retrieve a listing by ID and return the raw response."""
        response = self._client.request_raw("GET", f"/v1/listings/{listing_id}")
        return RawResponse(response, ListingDetailResponse)

    def update(self, listing_id: str, **kwargs: Any) -> RawResponse[ListingDetailResponse]:
        """Update a listing and return the raw response."""
        body = {k: v for k, v in kwargs.items() if v is not None}
        response = self._client.request_raw("PUT", f"/v1/listings/{listing_id}", json=body)
        return RawResponse(response, ListingDetailResponse)

    def publish(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Publish a draft listing and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/listings/{listing_id}/publish")
        return RawResponse(response, ListingDetailResponse)

    def unpublish(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Unpublish a listing and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/listings/{listing_id}/unpublish")
        return RawResponse(response, ListingDetailResponse)

    def archive(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Archive a listing and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/listings/{listing_id}/archive")
        return RawResponse(response, ListingDetailResponse)


class _AsyncRawListingsProxy:
    """Async proxy that calls Listings methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Retrieve a listing by ID and return the raw response (async)."""
        response = await self._client.request_raw("GET", f"/v1/listings/{listing_id}")
        return RawResponse(response, ListingDetailResponse)

    async def update(self, listing_id: str, **kwargs: Any) -> RawResponse[ListingDetailResponse]:
        """Update a listing and return the raw response (async)."""
        body = {k: v for k, v in kwargs.items() if v is not None}
        response = await self._client.request_raw("PUT", f"/v1/listings/{listing_id}", json=body)
        return RawResponse(response, ListingDetailResponse)

    async def publish(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Publish a draft listing and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/listings/{listing_id}/publish")
        return RawResponse(response, ListingDetailResponse)

    async def unpublish(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Unpublish a listing and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/listings/{listing_id}/unpublish")
        return RawResponse(response, ListingDetailResponse)

    async def archive(self, listing_id: str) -> RawResponse[ListingDetailResponse]:
        """Archive a listing and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/listings/{listing_id}/archive")
        return RawResponse(response, ListingDetailResponse)


class Listings:
    """Sync resource for the /v1/listings endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawListingsProxy:
        """Access listing methods that return raw HTTP responses instead of parsed models."""
        return _RawListingsProxy(self._client)

    def create(
        self,
        *,
        name: str,
        price: int,
        deliverable: Any | None = None,
        agent_callback_url: str | None = None,
        signing_secret: str | None = None,
        checkout_schema: list[Any] | None = None,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        image_url: str | None = None,
        currency: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
        timeout: float | None = None,
    ) -> ListingCreateResponse:
        """Create a new listing.

        Builds the request body from non-None params. Returns a
        :class:`~listbee.types.listing_create.ListingCreateResponse` envelope containing
        the listing and a one-time ``signing_secret``. Store the secret immediately.

        ``fulfillment_mode`` is computed server-side from deliverable presence:
        ``MANAGED`` when a deliverable is attached, ``ASYNC`` otherwise.

        Args:
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            deliverable: Single digital deliverable. Use :class:`~listbee.Deliverable`
                builder: ``Deliverable.url("https://...")`` or ``Deliverable.text("...")``.
            agent_callback_url: Optional HTTPS URL that receives ``order.paid`` /
                ``order.fulfilled`` webhooks.
            signing_secret: Optional custom signing secret for webhook verification.
                If omitted, ListBee generates one (shown once in the response).
            checkout_schema: Custom fields collected at checkout. Each element can be a
                :class:`~listbee.CheckoutField` builder or a raw dict. Max 10 fields.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text. Defaults to "Buy Now" when not set.
            image_url: Cover image URL (https://). Shown on the product page.
            currency: ISO 4217 lowercase currency code (e.g. "usd"). Defaults to account currency.
            metadata: Arbitrary key-value pairs forwarded in webhook events.
                Stripe-aligned limits: max 50 keys, keys ≤ 40 chars, string values ≤ 500 chars.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.
            timeout: Request timeout in seconds. Defaults to
                ``LISTING_CREATE_TIMEOUT`` (120s).

        Returns:
            :class:`~listbee.types.listing_create.ListingCreateResponse` with ``listing``
            (:class:`~listbee.types.listing.ListingBase`) and one-time ``signing_secret``.
        """
        body: dict[str, Any] = {
            "name": name,
            "price": price,
        }
        if deliverable is not None:
            body["deliverable"] = _resolve_deliverable(deliverable)
        if agent_callback_url is not None:
            body["agent_callback_url"] = agent_callback_url
        if signing_secret is not None:
            body["signing_secret"] = signing_secret
        if checkout_schema is not None:
            body["checkout_schema"] = _resolve_checkout_schema(checkout_schema)
        if description is not None:
            body["description"] = description
        if tagline is not None:
            body["tagline"] = tagline
        if highlights is not None:
            body["highlights"] = highlights
        if cta is not None:
            body["cta"] = cta
        if image_url is not None:
            body["image_url"] = image_url
        if currency is not None:
            body["currency"] = currency
        if metadata is not None:
            body["metadata"] = metadata
        if compare_at_price is not None:
            body["compare_at_price"] = compare_at_price
        if badges is not None:
            body["badges"] = badges
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
        return ListingCreateResponse.model_validate(response.json())

    def get(self, listing_id: str) -> ListingDetailResponse:
        """Retrieve a listing by its ID.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            :class:`~listbee.types.listing.ListingDetailResponse` for that listing (includes stats).
        """
        response = self._client.get(f"/v1/listings/{listing_id}")
        return ListingDetailResponse.model_validate(response.json())

    def list(
        self, *, limit: int = 20, cursor: str | None = None, status: str | None = None
    ) -> SyncCursorPage[ListingSummary]:
        """Return a paginated list of listings.

        Each item is a :class:`~listbee.types.listing.ListingSummary` with the core fields
        needed to display listing cards. Call :meth:`get` with the listing ID for the full
        :class:`~listbee.types.listing.ListingDetailResponse` including stats and deliverable.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for listing in client.listings.list():
                print(listing.name)

        Args:
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.
            status: Filter listings by status (e.g. "published", "draft", "archived").

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.listing.ListingSummary` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        return self._client.get_page("/v1/listings", params, ListingSummary)

    def update(
        self,
        listing_id: str,
        *,
        name: str | None = None,
        price: int | None = None,
        deliverable: Any | None = None,
        agent_callback_url: str | None = None,
        signing_secret: str | None = None,
        checkout_schema: list[Any] | None = None,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        image_url: str | None = None,
        currency: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
    ) -> ListingDetailResponse | RotateSigningSecretResponse:
        """Update an existing listing.

        Only the supplied fields are updated; all others remain unchanged.

        To rotate the signing secret, pass ``signing_secret="rotate"``. The response will be a
        :class:`~listbee.types.listing_create.RotateSigningSecretResponse` envelope (use
        ``isinstance(result, RotateSigningSecretResponse)`` to detect).

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            deliverable: Single digital deliverable. Use :class:`~listbee.Deliverable`
                builder: ``Deliverable.url("https://...")`` or ``Deliverable.text("...")``.
            agent_callback_url: HTTPS URL for ``order.paid`` / ``order.fulfilled`` webhooks.
            signing_secret: Pass ``"rotate"`` to rotate the webhook signing secret
                (returns :class:`~listbee.types.listing_create.RotateSigningSecretResponse`).
            checkout_schema: Custom fields collected at checkout. Max 10 fields.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text.
            image_url: Cover image URL (https://).
            currency: ISO 4217 lowercase currency code (e.g. "usd").
            metadata: Arbitrary key-value pairs forwarded in webhook events.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.

        Returns:
            :class:`~listbee.types.listing.ListingDetailResponse` normally, or
            :class:`~listbee.types.listing_create.RotateSigningSecretResponse` when
            ``signing_secret="rotate"`` is passed.
        """
        body: dict[str, Any] = {}
        fields: dict[str, Any] = {
            "name": name,
            "price": price,
            "agent_callback_url": agent_callback_url,
            "signing_secret": signing_secret,
            "checkout_schema": _resolve_checkout_schema(checkout_schema),
            "description": description,
            "tagline": tagline,
            "highlights": highlights,
            "cta": cta,
            "image_url": image_url,
            "currency": currency,
            "metadata": metadata,
            "compare_at_price": compare_at_price,
            "badges": badges,
            "rating": rating,
            "rating_count": rating_count,
            "reviews": reviews,
            "faqs": faqs,
        }
        if deliverable is not None:
            body["deliverable"] = _resolve_deliverable(deliverable)
        for key, value in fields.items():
            if value is not None:
                body[key] = value
        response = self._client.put(f"/v1/listings/{listing_id}", json=body)
        data = response.json()
        if data.get("object") == "rotate_signing_secret":
            return RotateSigningSecretResponse.model_validate(data)
        return ListingDetailResponse.model_validate(data)

    def delete(self, listing_id: str) -> None:
        """Delete a listing.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
        """
        self._client.delete(f"/v1/listings/{listing_id}")

    def publish(self, listing_id: str) -> ListingDetailResponse:
        """Publish a draft listing, making it live and buyable.

        Fails with 409 if readiness requirements are not met.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The published :class:`~listbee.types.listing.ListingDetailResponse`.
        """
        response = self._client.post(f"/v1/listings/{listing_id}/publish")
        return ListingDetailResponse.model_validate(response.json())

    def unpublish(self, listing_id: str) -> ListingDetailResponse:
        """Unpublish a listing, reverting it to draft.

        The listing will no longer be visible to buyers. Use :meth:`publish`
        to make it live again.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The updated :class:`~listbee.types.listing.ListingDetailResponse` with status ``draft``.
        """
        response = self._client.post(f"/v1/listings/{listing_id}/unpublish")
        return ListingDetailResponse.model_validate(response.json())

    def archive(self, listing_id: str) -> ListingDetailResponse:
        """Archive a listing, removing it from active management.

        Archived listings are no longer visible to buyers and cannot be purchased.
        Use this for discontinued products.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The updated :class:`~listbee.types.listing.ListingDetailResponse` with status ``archived``.
        """
        response = self._client.post(f"/v1/listings/{listing_id}/archive")
        return ListingDetailResponse.model_validate(response.json())


class AsyncListings:
    """Async resource for the /v1/listings endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawListingsProxy:
        """Access listing methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawListingsProxy(self._client)

    async def create(
        self,
        *,
        name: str,
        price: int,
        deliverable: Any | None = None,
        agent_callback_url: str | None = None,
        signing_secret: str | None = None,
        checkout_schema: list[Any] | None = None,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        image_url: str | None = None,
        currency: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
        timeout: float | None = None,
    ) -> ListingCreateResponse:
        """Create a new listing (async).

        Returns a :class:`~listbee.types.listing_create.ListingCreateResponse` envelope
        containing the listing and a one-time ``signing_secret``. Store the secret immediately.

        Args:
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            deliverable: Single digital deliverable. Use :class:`~listbee.Deliverable`
                builder: ``Deliverable.url("https://...")`` or ``Deliverable.text("...")``.
            agent_callback_url: HTTPS URL for ``order.paid`` / ``order.fulfilled`` webhooks.
            signing_secret: Optional custom signing secret for webhook verification.
            checkout_schema: Custom fields collected at checkout. Max 10 fields.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text. Defaults to "Buy Now" when not set.
            image_url: Cover image URL (https://).
            currency: ISO 4217 lowercase currency code (e.g. "usd").
            metadata: Arbitrary key-value pairs forwarded in webhook events.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.
            timeout: Request timeout in seconds (default: ``LISTING_CREATE_TIMEOUT``).

        Returns:
            :class:`~listbee.types.listing_create.ListingCreateResponse` with ``listing``
            (:class:`~listbee.types.listing.ListingBase`) and one-time ``signing_secret``.
        """
        body: dict[str, Any] = {
            "name": name,
            "price": price,
        }
        if deliverable is not None:
            body["deliverable"] = _resolve_deliverable(deliverable)
        if agent_callback_url is not None:
            body["agent_callback_url"] = agent_callback_url
        if signing_secret is not None:
            body["signing_secret"] = signing_secret
        if checkout_schema is not None:
            body["checkout_schema"] = _resolve_checkout_schema(checkout_schema)
        if description is not None:
            body["description"] = description
        if tagline is not None:
            body["tagline"] = tagline
        if highlights is not None:
            body["highlights"] = highlights
        if cta is not None:
            body["cta"] = cta
        if image_url is not None:
            body["image_url"] = image_url
        if currency is not None:
            body["currency"] = currency
        if metadata is not None:
            body["metadata"] = metadata
        if compare_at_price is not None:
            body["compare_at_price"] = compare_at_price
        if badges is not None:
            body["badges"] = badges
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
        return ListingCreateResponse.model_validate(response.json())

    async def get(self, listing_id: str) -> ListingDetailResponse:
        """Retrieve a listing by its ID (async).

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            :class:`~listbee.types.listing.ListingDetailResponse` for that listing (includes stats).
        """
        response = await self._client.get(f"/v1/listings/{listing_id}")
        return ListingDetailResponse.model_validate(response.json())

    async def list(
        self, *, limit: int = 20, cursor: str | None = None, status: str | None = None
    ) -> AsyncCursorPage[ListingSummary]:
        """Return a paginated list of listings (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for listing in await client.listings.list():
                print(listing.name)

        Args:
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.
            status: Filter listings by status (e.g. "published", "draft", "archived").

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.listing.ListingSummary` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        return await self._client.get_page("/v1/listings", params, ListingSummary)

    async def update(
        self,
        listing_id: str,
        *,
        name: str | None = None,
        price: int | None = None,
        deliverable: Any | None = None,
        agent_callback_url: str | None = None,
        signing_secret: str | None = None,
        checkout_schema: list[Any] | None = None,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        image_url: str | None = None,
        currency: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
    ) -> ListingDetailResponse | RotateSigningSecretResponse:
        """Update an existing listing (async).

        Only the supplied fields are updated; all others remain unchanged.
        Pass ``signing_secret="rotate"`` to rotate the signing secret.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            name: Product name shown on the product page.
            price: Price in the smallest currency unit.
            deliverable: Single digital deliverable.
            agent_callback_url: HTTPS URL for webhook delivery.
            signing_secret: Pass ``"rotate"`` to rotate the signing secret.
            checkout_schema: Custom checkout fields. Max 10.
            description: Product description.
            tagline: Short tagline.
            highlights: Bullet-point feature badges.
            cta: Buy button text.
            image_url: Cover image URL (https://).
            currency: ISO 4217 lowercase currency code.
            metadata: Arbitrary key-value pairs.
            compare_at_price: Strikethrough price.
            badges: Promotional badges.
            rating: Star rating (1-5).
            rating_count: Review/purchase count.
            reviews: Featured review cards.
            faqs: FAQ accordion items.

        Returns:
            :class:`~listbee.types.listing.ListingDetailResponse` normally, or
            :class:`~listbee.types.listing_create.RotateSigningSecretResponse` when
            ``signing_secret="rotate"`` is passed.
        """
        body: dict[str, Any] = {}
        fields: dict[str, Any] = {
            "name": name,
            "price": price,
            "agent_callback_url": agent_callback_url,
            "signing_secret": signing_secret,
            "checkout_schema": _resolve_checkout_schema(checkout_schema),
            "description": description,
            "tagline": tagline,
            "highlights": highlights,
            "cta": cta,
            "image_url": image_url,
            "currency": currency,
            "metadata": metadata,
            "compare_at_price": compare_at_price,
            "badges": badges,
            "rating": rating,
            "rating_count": rating_count,
            "reviews": reviews,
            "faqs": faqs,
        }
        if deliverable is not None:
            body["deliverable"] = _resolve_deliverable(deliverable)
        for key, value in fields.items():
            if value is not None:
                body[key] = value
        response = await self._client.put(f"/v1/listings/{listing_id}", json=body)
        data = response.json()
        if data.get("object") == "rotate_signing_secret":
            return RotateSigningSecretResponse.model_validate(data)
        return ListingDetailResponse.model_validate(data)

    async def delete(self, listing_id: str) -> None:
        """Delete a listing (async).

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
        """
        await self._client.delete(f"/v1/listings/{listing_id}")

    async def publish(self, listing_id: str) -> ListingDetailResponse:
        """Publish a draft listing, making it live and buyable (async).

        Fails with 409 if readiness requirements are not met.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The published :class:`~listbee.types.listing.ListingDetailResponse`.
        """
        response = await self._client.post(f"/v1/listings/{listing_id}/publish")
        return ListingDetailResponse.model_validate(response.json())

    async def unpublish(self, listing_id: str) -> ListingDetailResponse:
        """Unpublish a listing, reverting it to draft (async).

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The updated :class:`~listbee.types.listing.ListingDetailResponse` with status ``draft``.
        """
        response = await self._client.post(f"/v1/listings/{listing_id}/unpublish")
        return ListingDetailResponse.model_validate(response.json())

    async def archive(self, listing_id: str) -> ListingDetailResponse:
        """Archive a listing, removing it from active management (async).

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The updated :class:`~listbee.types.listing.ListingDetailResponse` with status ``archived``.
        """
        response = await self._client.post(f"/v1/listings/{listing_id}/archive")
        return ListingDetailResponse.model_validate(response.json())
