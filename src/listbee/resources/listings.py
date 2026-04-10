"""Listings resource — sync and async variants."""

from __future__ import annotations

import mimetypes
from typing import TYPE_CHECKING, Any, BinaryIO

from listbee._constants import LISTING_CREATE_TIMEOUT
from listbee._exceptions import ListBeeError
from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee._raw_response import RawResponse
from listbee.types.listing import ListingResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient
    from listbee.deliverable import Deliverable
    from listbee.types.shared import DeliverableResponse

# Accepted image MIME types for cover uploads
_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}

_MAX_URL_REDIRECTS = 3
_URL_FETCH_TIMEOUT = 30.0


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
    ) -> RawResponse[ListingResponse]:
        """Create a new listing and return the raw response."""
        body = {"name": name, "price": price, **{k: v for k, v in kwargs.items() if v is not None}}
        response = self._client.request_raw("POST", "/v1/listings", json=body)
        return RawResponse(response, ListingResponse)

    def get(self, listing_id: str) -> RawResponse[ListingResponse]:
        """Retrieve a listing by ID and return the raw response."""
        response = self._client.request_raw("GET", f"/v1/listings/{listing_id}")
        return RawResponse(response, ListingResponse)

    def update(self, listing_id: str, **kwargs: Any) -> RawResponse[ListingResponse]:
        """Update a listing and return the raw response."""
        body = {k: v for k, v in kwargs.items() if v is not None}
        response = self._client.request_raw("PUT", f"/v1/listings/{listing_id}", json=body)
        return RawResponse(response, ListingResponse)

    def publish(self, listing_id: str) -> RawResponse[ListingResponse]:
        """Publish a draft listing and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/listings/{listing_id}/publish")
        return RawResponse(response, ListingResponse)


class _AsyncRawListingsProxy:
    """Async proxy that calls Listings methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self, listing_id: str) -> RawResponse[ListingResponse]:
        """Retrieve a listing by ID and return the raw response (async)."""
        response = await self._client.request_raw("GET", f"/v1/listings/{listing_id}")
        return RawResponse(response, ListingResponse)

    async def update(self, listing_id: str, **kwargs: Any) -> RawResponse[ListingResponse]:
        """Update a listing and return the raw response (async)."""
        body = {k: v for k, v in kwargs.items() if v is not None}
        response = await self._client.request_raw("PUT", f"/v1/listings/{listing_id}", json=body)
        return RawResponse(response, ListingResponse)

    async def publish(self, listing_id: str) -> RawResponse[ListingResponse]:
        """Publish a draft listing and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/listings/{listing_id}/publish")
        return RawResponse(response, ListingResponse)


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
        deliverable: str | None = None,
        fulfillment_url: str | None = None,
        checkout_schema: list[Any] | None = None,
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
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        timeout: float | None = None,
    ) -> ListingResponse:
        """Create a new listing.

        Builds the request body from non-None params. ``cover_blur`` is only
        included when it differs from the API default of ``"auto"``.

        Currency is inherited from the account, so it is not specified here.

        Args:
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            deliverable: File URL, redirect URL, or plain text to deliver after
                purchase. ListBee delivers this to buyers on payment.
            fulfillment_url: Optional URL called after payment to trigger external
                fulfillment. When set, ListBee POSTs the order to this URL after
                the buyer pays.
            checkout_schema: Custom fields collected at checkout. Each dict should
                have ``name``, ``label``, ``type``, and optionally ``required``
                and ``options``. Max 10 fields.
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
            utm_source: UTM source tag attached to checkout links (e.g. "twitter").
            utm_medium: UTM medium tag attached to checkout links (e.g. "social").
            utm_campaign: UTM campaign tag attached to checkout links (e.g. "launch-week").
            timeout: Request timeout in seconds. Defaults to
                ``LISTING_CREATE_TIMEOUT`` (120s) because cover processing can
                take a while.

        Returns:
            The created :class:`~listbee.types.listing.ListingResponse`.
        """
        body: dict[str, Any] = {
            "name": name,
            "price": price,
        }
        if deliverable is not None:
            body["deliverable"] = deliverable
        if fulfillment_url is not None:
            body["fulfillment_url"] = fulfillment_url
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
        if utm_source is not None:
            body["utm_source"] = utm_source
        if utm_medium is not None:
            body["utm_medium"] = utm_medium
        if utm_campaign is not None:
            body["utm_campaign"] = utm_campaign

        effective_timeout = timeout if timeout is not None else LISTING_CREATE_TIMEOUT
        response = self._client.post("/v1/listings", json=body, timeout=effective_timeout)
        return ListingResponse.model_validate(response.json())

    def create_complete(
        self,
        *,
        name: str,
        price: int,
        deliverables: list[Any] | None = None,
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
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        checkout_schema: list[Any] | None = None,
        timeout: float | None = None,
    ) -> ListingResponse:
        """Create a complete listing with deliverables in one call.

        Orchestrates: create listing, upload files, attach deliverables, return.
        If any step after listing creation fails, raises
        :class:`~listbee.PartialCreationError` with the ``listing_id``.

        Args:
            name: Product name.
            price: Price in cents.
            deliverables: List of :class:`~listbee.deliverable.Deliverable` objects.
            description: Product description.
            tagline: Short tagline.
            highlights: Feature bullet points.
            cta: Call-to-action button text.
            cover_url: URL of cover image.
            metadata: Arbitrary metadata forwarded in webhooks.
            compare_at_price: Strikethrough price in cents.
            badges: Promotional badges.
            cover_blur: Cover blur mode.
            rating: Star rating (1-5).
            rating_count: Review count.
            reviews: Featured review cards.
            faqs: FAQ items.
            utm_source: UTM source.
            utm_medium: UTM medium.
            utm_campaign: UTM campaign.
            checkout_schema: Custom checkout fields.
            timeout: Upload timeout.

        Returns:
            The complete :class:`~listbee.types.listing.ListingResponse`.
        """
        from listbee._exceptions import PartialCreationError

        listing = self.create(
            name=name,
            price=price,
            description=description,
            tagline=tagline,
            highlights=highlights,
            cta=cta,
            cover_url=cover_url,
            metadata=metadata,
            compare_at_price=compare_at_price,
            badges=badges,
            cover_blur=cover_blur,
            rating=rating,
            rating_count=rating_count,
            reviews=reviews,
            faqs=faqs,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            checkout_schema=checkout_schema,
            timeout=timeout,
        )

        if not deliverables:
            return listing

        try:
            for d in deliverables:
                self.add_deliverable(listing.id, d, timeout=timeout)
            return self.get(listing.id)
        except Exception as e:
            raise PartialCreationError(listing.id, str(e)) from e

    def get(self, listing_id: str) -> ListingResponse:
        """Retrieve a listing by its ID.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The :class:`~listbee.types.listing.ListingResponse` for that listing.
        """
        response = self._client.get(f"/v1/listings/{listing_id}")
        return ListingResponse.model_validate(response.json())

    def list(
        self, *, limit: int = 20, cursor: str | None = None, status: str | None = None
    ) -> SyncCursorPage[ListingResponse]:
        """Return a paginated list of listings.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for listing in client.listings.list():
                print(listing.name)

        Args:
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.
            status: Filter listings by status (e.g. "published", "draft").

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.listing.ListingResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        return self._client.get_page("/v1/listings", params, ListingResponse)

    def update(
        self,
        listing_id: str,
        *,
        name: str | None = None,
        price: int | None = None,
        fulfillment_url: str | None = None,
        checkout_schema: list[Any] | None = None,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        cover_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        cover_blur: str | None = None,
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
    ) -> ListingResponse:
        """Update an existing listing.

        Only the supplied fields are updated; all others remain unchanged.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            fulfillment_url: Optional URL for external fulfillment. Set to a URL to
                enable external fulfillment; omit to use ListBee's managed delivery.
            checkout_schema: Custom fields collected at checkout. Max 10 fields.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text.
            cover_url: URL of a cover image to fetch and store.
            metadata: Arbitrary key-value pairs forwarded in webhook events.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            cover_blur: Cover blur mode — "auto", "true", or "false".
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.
            utm_source: UTM source tag attached to checkout links (e.g. "twitter").
            utm_medium: UTM medium tag attached to checkout links (e.g. "social").
            utm_campaign: UTM campaign tag attached to checkout links (e.g. "launch-week").

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.
        """
        body: dict[str, Any] = {}
        fields = {
            "name": name,
            "price": price,
            "fulfillment_url": fulfillment_url,
            "checkout_schema": _resolve_checkout_schema(checkout_schema),
            "description": description,
            "tagline": tagline,
            "highlights": highlights,
            "cta": cta,
            "cover_url": cover_url,
            "metadata": metadata,
            "compare_at_price": compare_at_price,
            "badges": badges,
            "cover_blur": cover_blur,
            "rating": rating,
            "rating_count": rating_count,
            "reviews": reviews,
            "faqs": faqs,
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
        }
        for key, value in fields.items():
            if value is not None:
                body[key] = value
        response = self._client.put(f"/v1/listings/{listing_id}", json=body)
        return ListingResponse.model_validate(response.json())

    def delete(self, listing_id: str) -> None:
        """Delete a listing.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
        """
        self._client.delete(f"/v1/listings/{listing_id}")

    def set_deliverables(
        self,
        listing_id: str,
        *,
        deliverables: list[Any],
    ) -> ListingResponse:
        """Replace all deliverables on a draft listing.

        Accepts :class:`~listbee.deliverable.Deliverable` objects or raw dicts.
        Files are uploaded transparently before sending the request.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            deliverables: List of Deliverable objects or dicts with ``type``
                and ``token``/``value``.

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.
        """
        from listbee.deliverable import Deliverable as DeliverableInput
        from listbee.resources.files import Files

        resolved: list[dict[str, Any]] = []
        files_resource = Files(self._client)
        for d in deliverables:
            if isinstance(d, DeliverableInput):
                token = None
                if d.needs_upload:
                    file_resp = files_resource.upload(file=d.to_upload_tuple())
                    token = file_resp.id
                resolved.append(d.to_api_body(token=token))
            else:
                resolved.append(d)
        body: dict[str, Any] = {"deliverables": resolved}
        response = self._client.put(f"/v1/listings/{listing_id}/deliverables", json=body)
        return ListingResponse.model_validate(response.json())

    def remove_deliverables(self, listing_id: str) -> ListingResponse:
        """Remove all deliverables from a draft listing.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.
        """
        response = self._client.delete(f"/v1/listings/{listing_id}/deliverables")
        return ListingResponse.model_validate(response.json())

    def add_deliverable(
        self,
        listing_id: str,
        deliverable: Deliverable,
        *,
        timeout: float | None = None,
    ) -> DeliverableResponse:
        """Add a single deliverable to a draft listing.

        Accepts any deliverable type. Files are uploaded transparently.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            deliverable: A :class:`~listbee.deliverable.Deliverable` instance.
            timeout: Optional timeout for file upload.

        Returns:
            The new :class:`~listbee.types.shared.DeliverableResponse`.
        """
        from listbee.resources.files import Files
        from listbee.types.shared import DeliverableResponse

        token = None
        if deliverable.needs_upload:
            file_resp = Files(self._client).upload(file=deliverable.to_upload_tuple(), timeout=timeout)
            token = file_resp.id
        body = deliverable.to_api_body(token=token)
        response = self._client.post(f"/v1/listings/{listing_id}/deliverables", json=body)
        return DeliverableResponse.model_validate(response.json())

    def remove_deliverable(self, listing_id: str, deliverable_id: str) -> None:
        """Remove a single deliverable by ID from a draft listing.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            deliverable_id: The deliverable's ID (e.g. "del_7kQ2xY9mN3pR5tW1vB8a").
        """
        self._client.delete(f"/v1/listings/{listing_id}/deliverables/{deliverable_id}")

    def publish(self, listing_id: str) -> ListingResponse:
        """Publish a draft listing, making it live and buyable.

        Fails with 409 if readiness requirements are not met.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The published :class:`~listbee.types.listing.ListingResponse`.
        """
        response = self._client.post(f"/v1/listings/{listing_id}/publish")
        return ListingResponse.model_validate(response.json())

    def set_cover(self, listing_id: str, source: str | BinaryIO | bytes) -> ListingResponse:
        """Set the listing cover image from a file token, URL, or binary content.

        Accepts three input forms:

        * **File token** (``file_`` prefix) — passed directly to listing update.
          Upload via ``client.files.upload(purpose="cover")`` first.
        * **URL** (``http://`` / ``https://``) — fetched, validated as an image,
          uploaded with ``purpose="cover"``, then applied.
        * **bytes / BinaryIO** — uploaded with ``purpose="cover"``, then applied.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            source: A ``file_`` token, an image URL, raw bytes, or a file-like object.

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.

        Raises:
            ListBeeError: If the URL fetch fails, returns a non-image content type,
                or the upload/update request fails.
        """
        import httpx as _httpx

        token = self._resolve_cover_source(listing_id, source, _httpx)
        return self.update(listing_id, cover_url=token)

    def _resolve_cover_source(self, listing_id: str, source: str | BinaryIO | bytes, _httpx: Any) -> str:
        """Upload (if needed) and return a file_ token for the cover."""
        from listbee.resources.files import Files

        files_resource = Files(self._client)

        if isinstance(source, str) and source.startswith("file_"):
            return source

        if isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
            with _httpx.Client(follow_redirects=True, max_redirects=_MAX_URL_REDIRECTS) as http:
                try:
                    resp = http.get(source, timeout=_URL_FETCH_TIMEOUT)
                except _httpx.TimeoutException as exc:
                    raise ListBeeError(f"Timed out fetching cover URL: {source}") from exc
                except _httpx.RequestError as exc:
                    raise ListBeeError(f"Failed to fetch cover URL: {source} — {exc}") from exc
                if resp.is_error:
                    raise ListBeeError(f"Failed to fetch cover URL: {source} — HTTP {resp.status_code}")
                content_type = resp.headers.get("content-type", "").split(";")[0].strip()
                if content_type not in _IMAGE_MIME_TYPES:
                    raise ListBeeError(
                        f"URL did not return an image (got Content-Type: {content_type}): {source}"
                    )
                content = resp.content
                ext = mimetypes.guess_extension(content_type) or ".jpg"
                filename = f"cover{ext}"
                file_resp = files_resource.upload(file=(filename, content, content_type), purpose="cover")
                return file_resp.id

        # bytes or BinaryIO
        if isinstance(source, bytes):
            content = source
            filename = "cover.jpg"
            content_type = "image/jpeg"
        else:
            content = source.read()
            name = getattr(source, "name", "cover.jpg")
            filename = name if isinstance(name, str) else "cover.jpg"
            guessed, _ = mimetypes.guess_type(filename)
            content_type = guessed or "image/jpeg"

        file_resp = files_resource.upload(file=(filename, content, content_type), purpose="cover")
        return file_resp.id


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
        deliverable: str | None = None,
        fulfillment_url: str | None = None,
        checkout_schema: list[Any] | None = None,
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
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        timeout: float | None = None,
    ) -> ListingResponse:
        """Create a new listing (async).

        Builds the request body from non-None params. ``cover_blur`` is only
        included when it differs from the API default of ``"auto"``.

        Currency is inherited from the account, so it is not specified here.

        Args:
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            deliverable: File URL, redirect URL, or plain text to deliver after
                purchase. ListBee delivers this to buyers on payment.
            fulfillment_url: Optional URL called after payment to trigger external
                fulfillment. When set, ListBee POSTs the order to this URL after
                the buyer pays.
            checkout_schema: Custom fields collected at checkout. Each dict should
                have ``name``, ``label``, ``type``, and optionally ``required``
                and ``options``. Max 10 fields.
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
            utm_source: UTM source tag attached to checkout links (e.g. "twitter").
            utm_medium: UTM medium tag attached to checkout links (e.g. "social").
            utm_campaign: UTM campaign tag attached to checkout links (e.g. "launch-week").
            timeout: Request timeout in seconds. Defaults to
                ``LISTING_CREATE_TIMEOUT`` (120s) because cover processing can
                take a while.

        Returns:
            The created :class:`~listbee.types.listing.ListingResponse`.
        """
        body: dict[str, Any] = {
            "name": name,
            "price": price,
        }
        if deliverable is not None:
            body["deliverable"] = deliverable
        if fulfillment_url is not None:
            body["fulfillment_url"] = fulfillment_url
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
        if utm_source is not None:
            body["utm_source"] = utm_source
        if utm_medium is not None:
            body["utm_medium"] = utm_medium
        if utm_campaign is not None:
            body["utm_campaign"] = utm_campaign

        effective_timeout = timeout if timeout is not None else LISTING_CREATE_TIMEOUT
        response = await self._client.post("/v1/listings", json=body, timeout=effective_timeout)
        return ListingResponse.model_validate(response.json())

    async def create_complete(
        self,
        *,
        name: str,
        price: int,
        deliverables: list[Any] | None = None,
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
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        checkout_schema: list[Any] | None = None,
        timeout: float | None = None,
    ) -> ListingResponse:
        """Create a complete listing with deliverables in one call (async).

        Orchestrates: create listing, upload files, attach deliverables, return.
        If any step after listing creation fails, raises
        :class:`~listbee.PartialCreationError` with the ``listing_id``.

        Args:
            name: Product name.
            price: Price in cents.
            deliverables: List of :class:`~listbee.deliverable.Deliverable` objects.
            description: Product description.
            tagline: Short tagline.
            highlights: Feature bullet points.
            cta: Call-to-action button text.
            cover_url: URL of cover image.
            metadata: Arbitrary metadata forwarded in webhooks.
            compare_at_price: Strikethrough price in cents.
            badges: Promotional badges.
            cover_blur: Cover blur mode.
            rating: Star rating (1-5).
            rating_count: Review count.
            reviews: Featured review cards.
            faqs: FAQ items.
            utm_source: UTM source.
            utm_medium: UTM medium.
            utm_campaign: UTM campaign.
            checkout_schema: Custom checkout fields.
            timeout: Upload timeout.

        Returns:
            The complete :class:`~listbee.types.listing.ListingResponse`.
        """
        from listbee._exceptions import PartialCreationError

        listing = await self.create(
            name=name,
            price=price,
            description=description,
            tagline=tagline,
            highlights=highlights,
            cta=cta,
            cover_url=cover_url,
            metadata=metadata,
            compare_at_price=compare_at_price,
            badges=badges,
            cover_blur=cover_blur,
            rating=rating,
            rating_count=rating_count,
            reviews=reviews,
            faqs=faqs,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            checkout_schema=checkout_schema,
            timeout=timeout,
        )

        if not deliverables:
            return listing

        try:
            for d in deliverables:
                await self.add_deliverable(listing.id, d, timeout=timeout)
            return await self.get(listing.id)
        except Exception as e:
            raise PartialCreationError(listing.id, str(e)) from e

    async def get(self, listing_id: str) -> ListingResponse:
        """Retrieve a listing by its ID (async).

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The :class:`~listbee.types.listing.ListingResponse` for that listing.
        """
        response = await self._client.get(f"/v1/listings/{listing_id}")
        return ListingResponse.model_validate(response.json())

    async def list(
        self, *, limit: int = 20, cursor: str | None = None, status: str | None = None
    ) -> AsyncCursorPage[ListingResponse]:
        """Return a paginated list of listings (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for listing in await client.listings.list():
                print(listing.name)

        Args:
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.
            status: Filter listings by status (e.g. "published", "draft").

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.listing.ListingResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        return await self._client.get_page("/v1/listings", params, ListingResponse)

    async def update(
        self,
        listing_id: str,
        *,
        name: str | None = None,
        price: int | None = None,
        fulfillment_url: str | None = None,
        checkout_schema: list[Any] | None = None,
        description: str | None = None,
        tagline: str | None = None,
        highlights: list[str] | None = None,
        cta: str | None = None,
        cover_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        compare_at_price: int | None = None,
        badges: list[str] | None = None,
        cover_blur: str | None = None,
        rating: float | None = None,
        rating_count: int | None = None,
        reviews: list[dict[str, Any]] | None = None,
        faqs: list[dict[str, Any]] | None = None,
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
    ) -> ListingResponse:
        """Update an existing listing (async).

        Only the supplied fields are updated; all others remain unchanged.

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            name: Product name shown on the product page.
            price: Price in the smallest currency unit (e.g. 2900 = $29.00).
            fulfillment_url: Optional URL for external fulfillment. Set to a URL to
                enable external fulfillment; omit to use ListBee's managed delivery.
            checkout_schema: Custom fields collected at checkout. Max 10 fields.
            description: Longer product description, plain text.
            tagline: Short line shown below the product name.
            highlights: Bullet-point feature badges shown on the product page.
            cta: Buy button text.
            cover_url: URL of a cover image to fetch and store.
            metadata: Arbitrary key-value pairs forwarded in webhook events.
            compare_at_price: Strikethrough price in smallest currency unit.
            badges: Short promotional badges shown on the product page.
            cover_blur: Cover blur mode — "auto", "true", or "false".
            rating: Seller-provided aggregate star rating (1–5).
            rating_count: Seller-provided review or purchase count.
            reviews: Featured review cards shown on the product page.
            faqs: FAQ accordion items shown on the product page.
            utm_source: UTM source tag attached to checkout links (e.g. "twitter").
            utm_medium: UTM medium tag attached to checkout links (e.g. "social").
            utm_campaign: UTM campaign tag attached to checkout links (e.g. "launch-week").

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.
        """
        body: dict[str, Any] = {}
        fields = {
            "name": name,
            "price": price,
            "fulfillment_url": fulfillment_url,
            "checkout_schema": _resolve_checkout_schema(checkout_schema),
            "description": description,
            "tagline": tagline,
            "highlights": highlights,
            "cta": cta,
            "cover_url": cover_url,
            "metadata": metadata,
            "compare_at_price": compare_at_price,
            "badges": badges,
            "cover_blur": cover_blur,
            "rating": rating,
            "rating_count": rating_count,
            "reviews": reviews,
            "faqs": faqs,
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
        }
        for key, value in fields.items():
            if value is not None:
                body[key] = value
        response = await self._client.put(f"/v1/listings/{listing_id}", json=body)
        return ListingResponse.model_validate(response.json())

    async def delete(self, listing_id: str) -> None:
        """Delete a listing (async).

        Args:
            listing_id: The listing's unique identifier (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
        """
        await self._client.delete(f"/v1/listings/{listing_id}")

    async def set_deliverables(
        self,
        listing_id: str,
        *,
        deliverables: list[Any],
    ) -> ListingResponse:
        """Replace all deliverables on a draft listing (async).

        Accepts :class:`~listbee.deliverable.Deliverable` objects or raw dicts.
        Files are uploaded transparently before sending the request.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            deliverables: List of Deliverable objects or dicts with ``type``
                and ``token``/``value``.

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.
        """
        from listbee.deliverable import Deliverable as DeliverableInput
        from listbee.resources.files import AsyncFiles

        resolved: list[dict[str, Any]] = []
        files_resource = AsyncFiles(self._client)
        for d in deliverables:
            if isinstance(d, DeliverableInput):
                token = None
                if d.needs_upload:
                    file_resp = await files_resource.upload(file=d.to_upload_tuple())
                    token = file_resp.id
                resolved.append(d.to_api_body(token=token))
            else:
                resolved.append(d)
        body: dict[str, Any] = {"deliverables": resolved}
        response = await self._client.put(f"/v1/listings/{listing_id}/deliverables", json=body)
        return ListingResponse.model_validate(response.json())

    async def remove_deliverables(self, listing_id: str) -> ListingResponse:
        """Remove all deliverables from a draft listing (async).

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.
        """
        response = await self._client.delete(f"/v1/listings/{listing_id}/deliverables")
        return ListingResponse.model_validate(response.json())

    async def add_deliverable(
        self,
        listing_id: str,
        deliverable: Deliverable,
        *,
        timeout: float | None = None,
    ) -> DeliverableResponse:
        """Add a single deliverable to a draft listing (async).

        Accepts any deliverable type. Files are uploaded transparently.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            deliverable: A :class:`~listbee.deliverable.Deliverable` instance.
            timeout: Optional timeout for file upload.

        Returns:
            The new :class:`~listbee.types.shared.DeliverableResponse`.
        """
        from listbee.resources.files import AsyncFiles
        from listbee.types.shared import DeliverableResponse

        token = None
        if deliverable.needs_upload:
            file_resp = await AsyncFiles(self._client).upload(file=deliverable.to_upload_tuple(), timeout=timeout)
            token = file_resp.id
        body = deliverable.to_api_body(token=token)
        response = await self._client.post(f"/v1/listings/{listing_id}/deliverables", json=body)
        return DeliverableResponse.model_validate(response.json())

    async def remove_deliverable(self, listing_id: str, deliverable_id: str) -> None:
        """Remove a single deliverable by ID from a draft listing (async).

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            deliverable_id: The deliverable's ID (e.g. "del_7kQ2xY9mN3pR5tW1vB8a").
        """
        await self._client.delete(f"/v1/listings/{listing_id}/deliverables/{deliverable_id}")

    async def publish(self, listing_id: str) -> ListingResponse:
        """Publish a draft listing, making it live and buyable (async).

        Fails with 409 if readiness requirements are not met.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").

        Returns:
            The published :class:`~listbee.types.listing.ListingResponse`.
        """
        response = await self._client.post(f"/v1/listings/{listing_id}/publish")
        return ListingResponse.model_validate(response.json())

    async def set_cover(self, listing_id: str, source: str | BinaryIO | bytes) -> ListingResponse:
        """Set the listing cover image from a file token, URL, or binary content (async).

        Accepts three input forms:

        * **File token** (``file_`` prefix) — passed directly to listing update.
          Upload via ``client.files.upload(purpose="cover")`` first.
        * **URL** (``http://`` / ``https://``) — fetched, validated as an image,
          uploaded with ``purpose="cover"``, then applied.
        * **bytes / BinaryIO** — uploaded with ``purpose="cover"``, then applied.

        Args:
            listing_id: The listing's ID (e.g. "lst_7kQ2xY9mN3pR5tW1vB8a").
            source: A ``file_`` token, an image URL, raw bytes, or a file-like object.

        Returns:
            The updated :class:`~listbee.types.listing.ListingResponse`.

        Raises:
            ListBeeError: If the URL fetch fails, returns a non-image content type,
                or the upload/update request fails.
        """
        import httpx as _httpx

        token = await self._resolve_cover_source(listing_id, source, _httpx)
        return await self.update(listing_id, cover_url=token)

    async def _resolve_cover_source(self, listing_id: str, source: str | BinaryIO | bytes, _httpx: Any) -> str:
        """Upload (if needed) and return a file_ token for the cover (async)."""
        from listbee.resources.files import AsyncFiles

        files_resource = AsyncFiles(self._client)

        if isinstance(source, str) and source.startswith("file_"):
            return source

        if isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
            async with _httpx.AsyncClient(follow_redirects=True, max_redirects=_MAX_URL_REDIRECTS) as http:
                try:
                    resp = await http.get(source, timeout=_URL_FETCH_TIMEOUT)
                except _httpx.TimeoutException as exc:
                    raise ListBeeError(f"Timed out fetching cover URL: {source}") from exc
                except _httpx.RequestError as exc:
                    raise ListBeeError(f"Failed to fetch cover URL: {source} — {exc}") from exc
                if resp.is_error:
                    raise ListBeeError(f"Failed to fetch cover URL: {source} — HTTP {resp.status_code}")
                content_type = resp.headers.get("content-type", "").split(";")[0].strip()
                if content_type not in _IMAGE_MIME_TYPES:
                    raise ListBeeError(
                        f"URL did not return an image (got Content-Type: {content_type}): {source}"
                    )
                content = resp.content
                ext = mimetypes.guess_extension(content_type) or ".jpg"
                filename = f"cover{ext}"
                file_resp = await files_resource.upload(file=(filename, content, content_type), purpose="cover")
                return file_resp.id

        # bytes or BinaryIO
        if isinstance(source, bytes):
            content = source
            filename = "cover.jpg"
            content_type = "image/jpeg"
        else:
            content = source.read()
            name = getattr(source, "name", "cover.jpg")
            filename = name if isinstance(name, str) else "cover.jpg"
            guessed, _ = mimetypes.guess_type(filename)
            content_type = guessed or "image/jpeg"

        file_resp = await files_resource.upload(file=(filename, content, content_type), purpose="cover")
        return file_resp.id
