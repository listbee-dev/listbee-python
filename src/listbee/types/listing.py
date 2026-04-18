"""Listing response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from listbee.types.shared import (
    CheckoutFieldResponse,
    DeliverableResponse,
    FulfillmentMode,
    ListingReadiness,
    ListingStatus,
)


class ListingSummary(BaseModel):
    """Lightweight listing object returned in list responses.

    Use :meth:`~listbee.resources.listings.Listings.get` to retrieve the full
    :class:`ListingDetailResponse` with stats and all detail fields.
    """

    object: Literal["listing"] = Field(
        default="listing",
        description="Object type discriminator. Always `listing`.",
        examples=["listing"],
    )
    id: str = Field(
        description="Unique listing ID (lst_ prefixed). Use this for GET /v1/listings/{id} to fetch full detail.",
        examples=["lst_7kQ2xY9mN3pR5tW1vB8a"],
    )
    url: str = Field(
        description="Shareable product page URL. Share this with buyers. ID is the routing key; slug is derived from name.",
        examples=["https://buy.listbee.so/l/lst_7kQ2xY9mN3pR5tW1vB8a/seo-playbook-2026"],
    )
    name: str = Field(
        description="Product name.",
        examples=["SEO Playbook 2026"],
    )
    tagline: str | None = Field(
        default=None,
        description="Short tagline shown below the product name. Null if not set.",
        examples=["Updated for 2026 algorithm changes"],
    )
    price: int = Field(
        description="Price in cents. $29 = 2900.",
        examples=[2900],
    )
    currency: str = Field(
        description="Three-letter ISO 4217 currency code (lowercase).",
        examples=["usd"],
    )
    compare_at_price: int | None = Field(
        default=None,
        description="Strikethrough price in cents. Null if not set.",
        examples=[4900],
    )
    cta: str | None = Field(
        default=None,
        description="Buy button text. Null means default 'Buy Now' is used.",
        examples=["Get Instant Access"],
    )
    badges: list[str] = Field(
        default_factory=list,
        description="Short promotional badges. Empty list if none set.",
        examples=[["Best seller"]],
    )
    highlights: list[str] = Field(
        default_factory=list,
        description="Bullet-point feature list. Empty list if none set.",
        examples=[["50+ pages", "Actionable tips"]],
    )
    status: ListingStatus = Field(
        description="Listing status: `draft`, `published`, or `archived`.",
        examples=["published"],
    )
    fulfillment_mode: FulfillmentMode = Field(
        description="`MANAGED` if a deliverable is attached; `ASYNC` if your agent handles fulfillment.",
        examples=["MANAGED"],
    )
    image_url: str | None = Field(
        default=None,
        description="Cover image URL. Null if not set.",
        examples=["https://cdn.example.com/covers/abc123.jpg"],
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp when the listing was created.",
    )

    @property
    def is_draft(self) -> bool:
        """True when the listing is in draft state (not visible to buyers)."""
        return self.status == ListingStatus.DRAFT

    @property
    def is_published(self) -> bool:
        """True when the listing is published and visible to buyers."""
        return self.status == ListingStatus.PUBLISHED

    @property
    def is_archived(self) -> bool:
        """True when the listing is archived and no longer active."""
        return self.status == ListingStatus.ARCHIVED


class Review(BaseModel):
    """A single buyer review card displayed on the listing product page."""

    name: str = Field(
        description="Reviewer display name.",
        examples=["Clara D."],
    )
    rating: float = Field(
        description="Star rating (1–5).",
        examples=[4.5],
    )
    content: str = Field(
        description="Review body text.",
        examples=["Excellent quality content."],
    )


class FaqItem(BaseModel):
    """A single FAQ accordion item displayed on the listing product page."""

    q: str = Field(
        description="Question text.",
        examples=["Is this for beginners?"],
    )
    a: str = Field(
        description="Answer text.",
        examples=["Yes, completely beginner-friendly."],
    )


class ListingStats(BaseModel):
    """Aggregate performance stats for a listing."""

    schema_version: int = Field(
        default=1,
        description="Stats schema version.",
    )
    views: int = Field(
        default=0,
        description="Total page views for this listing.",
        examples=[142],
    )
    purchases: int = Field(
        default=0,
        description="Total number of completed purchases.",
        examples=[17],
    )
    gmv_minor: int = Field(
        default=0,
        description="Gross merchandise value in cents (smallest currency unit).",
        examples=[49300],
    )


class ListingBase(BaseModel):
    """Listing fields returned to the owner. Returned by POST /v1/listings (inside envelope).

    Does not include stats — use :class:`ListingDetailResponse` (from GET/PUT) for stats.
    """

    object: Literal["listing"] = Field(
        default="listing",
        description="Object type discriminator. Always `listing`.",
        examples=["listing"],
    )
    id: str = Field(
        description="Unique listing ID (lst_ prefixed). Use this for all API operations.",
        examples=["lst_7kQ2xY9mN3pR5tW1vB8a"],
    )
    url: str = Field(
        description=(
            "Shareable product page URL in the form `/l/{id}/{slug}`. "
            "The slug is derived from the listing name at serialization time and is not persisted — "
            "the ID is the routing key. Share this URL with buyers."
        ),
        examples=["https://buy.listbee.so/l/lst_7kQ2xY9mN3pR5tW1vB8a/seo-playbook-2026"],
    )
    name: str = Field(
        description="Product name shown on the product page.",
        examples=["SEO Playbook 2026"],
    )
    price: int = Field(
        description="Price in cents (smallest currency unit). $29 = 2900.",
        examples=[2900],
    )
    currency: str = Field(
        description="Three-letter ISO 4217 currency code (lowercase).",
        examples=["usd"],
    )
    status: ListingStatus = Field(
        description="Listing lifecycle status: `draft`, `published`, or `archived`. Only published listings have a live checkout URL.",
        examples=["published"],
    )
    fulfillment_mode: FulfillmentMode = Field(
        description=(
            "Computed from deliverable presence. `MANAGED` when a deliverable is attached "
            "(ListBee delivers automatically). `ASYNC` when no deliverable — "
            "your agent handles delivery via POST /v1/orders/{order_id}/fulfill or webhook."
        ),
        examples=["MANAGED"],
    )
    image_url: str | None = Field(
        default=None,
        description="Cover image URL (https://). Shown prominently on the product page. Null if not set.",
        examples=["https://cdn.example.com/covers/abc123.jpg"],
    )
    agent_callback_url: str | None = Field(
        default=None,
        description="Per-listing webhook URL for order events (signed with this listing's signing_secret). Null if not set.",
        examples=["https://my-agent.example.com/fulfill"],
    )
    deliverable: DeliverableResponse | None = Field(
        default=None,
        description=(
            "The stored deliverable ListBee delivers automatically on payment. "
            "Null for ASYNC listings. Content is redacted on non-owner reads."
        ),
    )
    readiness: ListingReadiness = Field(
        description=(
            "Agent-facing readiness signal. Check `readiness.buyable` first — if false, "
            "`readiness.next` gives the highest-priority action code and `readiness.actions` "
            "lists each blocker with resolve instructions."
        ),
    )
    checkout_schema: list[CheckoutFieldResponse] | None = Field(
        default=None,
        description="Custom fields collected from the buyer at checkout. Null if no custom fields configured.",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Key-value pairs you attached at creation or update. Forwarded in webhook event payloads. Null if not set.",
        examples=[{"source": "n8n", "campaign": "launch-week"}],
    )
    tagline: str | None = Field(
        default=None,
        description="Short tagline shown below the product name on the product page.",
        examples=["Updated for 2026 algorithm changes"],
    )
    description: str | None = Field(
        default=None,
        description="Product description shown on the product page.",
    )
    highlights: list[str] = Field(
        default_factory=list,
        description="Bullet-point feature list shown on the product page. Empty list if none set.",
        examples=[["50+ pages", "Actionable tips"]],
    )
    faqs: list[FaqItem] = Field(
        default_factory=lambda: [],
        description="FAQ accordion items shown on the product page. Empty list if none set.",
    )
    cta: str | None = Field(
        default=None,
        description="Buy button text. Null means the default 'Buy Now' is used.",
        examples=["Get Instant Access"],
    )
    compare_at_price: int | None = Field(
        default=None,
        description="Strikethrough price in cents shown alongside the regular price. Null if not set.",
        examples=[4900],
    )
    badges: list[str] = Field(
        default_factory=list,
        description="Short promotional badges shown on the product page. Empty list if none set.",
        examples=[["Best seller", "Limited time"]],
    )
    rating: float | None = Field(
        default=None,
        description="Seller-provided aggregate star rating (1.0–5.0). Null if not set.",
        examples=[4.8],
    )
    rating_count: int | None = Field(
        default=None,
        description="Seller-provided review/purchase count shown alongside the rating. Null if not set.",
        examples=[1243],
    )
    reviews: list[Review] = Field(
        default_factory=lambda: [],
        description="Featured seller-provided review cards shown on the product page. Empty list if none set.",
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp when the listing was created.",
    )

    @property
    def is_draft(self) -> bool:
        """True when the listing is in draft state (not visible to buyers)."""
        return self.status == ListingStatus.DRAFT

    @property
    def is_published(self) -> bool:
        """True when the listing is published and visible to buyers."""
        return self.status == ListingStatus.PUBLISHED

    @property
    def is_archived(self) -> bool:
        """True when the listing is archived and no longer active."""
        return self.status == ListingStatus.ARCHIVED

    @property
    def checkout_url(self) -> str:
        """Full product page URL — share this with buyers."""
        return self.url


class ListingDetailResponse(ListingBase):
    """Full listing detail: base fields + stats.

    Returned by GET /v1/listings/{id} and PUT /v1/listings/{id}.
    """

    stats: ListingStats = Field(
        description="Aggregate performance stats for this listing: views, purchases, and gross merchandise value in cents.",
    )
