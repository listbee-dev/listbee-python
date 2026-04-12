"""Listing response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from listbee.types.shared import (
    BlurMode,
    CheckoutFieldResponse,
    DeliverableResponse,
    ListingReadiness,
    ListingStatus,
)


class ListingSummary(BaseModel):
    """Slim listing object returned in list responses.

    Use :meth:`~listbee.resources.listings.Listings.get` to retrieve the full
    :class:`ListingResponse` with deliverables, reviews, FAQs, and all other fields.
    """

    object: Literal["listing"] = Field(
        default="listing",
        description="Object type discriminator. Always `listing`.",
        examples=["listing"],
    )
    id: str = Field(
        description="Unique listing identifier.",
        examples=["lst_7kQ2xY9mN3pR5tW1vB8a"],
    )
    slug: str = Field(
        description="URL slug used on the product page.",
        examples=["seo-playbook"],
    )
    name: str = Field(
        description="Product name shown on the product page.",
        examples=["SEO Playbook 2026"],
    )
    tagline: str | None = Field(
        default=None,
        description="Short line shown below the product name.",
        examples=["Updated for 2026 algorithm changes"],
    )
    price: int = Field(
        description="Price in the smallest currency unit (e.g. 2900 = $29.00).",
        examples=[2900],
    )
    compare_at_price: int | None = Field(
        default=None,
        description="Strikethrough price in smallest currency unit.",
        examples=[3900],
    )
    cta: str | None = Field(
        default=None,
        description="Buy button text. Defaults to 'Buy Now' when not set.",
        examples=["Get Instant Access"],
    )
    badges: list[str] = Field(
        default_factory=list,
        description="Short promotional badges shown on the product page.",
        examples=[["Limited time", "Best seller"]],
    )
    highlights: list[str] = Field(
        default_factory=list,
        description="Bullet-point feature badges shown on the product page.",
        examples=[["50+ pages", "Actionable tips", "Free updates"]],
    )
    status: ListingStatus = Field(
        description="Current listing status.",
        examples=["draft"],
    )
    stock: int | None = Field(
        default=None,
        description="Available stock quantity. Null means unlimited.",
    )
    has_deliverables: bool = Field(
        description="`true` if one or more deliverables are attached to this listing.",
        examples=[True],
    )
    has_cover: bool = Field(
        description="`true` if a cover image exists (uploaded or auto-generated).",
        examples=[True],
    )
    url: str | None = Field(
        default=None,
        description="Full product page URL — share this with buyers.",
        examples=["https://buy.listbee.so/seo-playbook"],
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the listing was created.",
    )

    @property
    def is_draft(self) -> bool:
        """True when the listing is in draft state (not visible to buyers)."""
        return self.status == "draft"

    @property
    def is_published(self) -> bool:
        """True when the listing is published and visible to buyers."""
        return self.status == "published"

    @property
    def is_in_stock(self) -> bool:
        """True when the listing has available stock (or unlimited stock when stock is None)."""
        return self.stock is None or self.stock > 0


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


class ListingResponse(BaseModel):
    """Full listing object returned by the ListBee API."""

    object: Literal["listing"] = Field(
        default="listing",
        description="Object type discriminator. Always `listing`.",
        examples=["listing"],
    )
    id: str = Field(
        description="Unique listing identifier.",
        examples=["lst_7kQ2xY9mN3pR5tW1vB8a"],
    )
    slug: str = Field(
        description="URL slug used on the product page.",
        examples=["seo-playbook"],
    )
    name: str = Field(
        description="Product name shown on the product page.",
        examples=["SEO Playbook 2026"],
    )
    description: str | None = Field(
        default=None,
        description="Longer product description, plain text.",
        examples=["A comprehensive guide to modern SEO techniques."],
    )
    tagline: str | None = Field(
        default=None,
        description="Short line shown below the product name.",
        examples=["Updated for 2026 algorithm changes"],
    )
    highlights: list[str] = Field(
        default_factory=list,
        description="Bullet-point feature badges shown on the product page.",
        examples=[["50+ pages", "Actionable tips", "Free updates"]],
    )
    cta: str | None = Field(
        default=None,
        description="Buy button text. Defaults to 'Buy Now' when not set.",
        examples=["Get Instant Access"],
    )
    price: int = Field(
        description="Price in the smallest currency unit (e.g. 2900 = $29.00).",
        examples=[2900],
    )
    fulfillment_url: str | None = Field(
        default=None,
        description=(
            "Optional URL called after payment to trigger external fulfillment. "
            "When set, ListBee POSTs the order to this URL after the buyer pays. "
            "Null means ListBee handles delivery via attached deliverables."
        ),
        examples=["https://yourapp.com/webhooks/listbee/fulfill"],
    )
    has_deliverables: bool = Field(
        description="`true` if one or more deliverables are attached to this listing.",
        examples=[True],
    )
    deliverables: list[DeliverableResponse] = Field(
        default=[],
        description=(
            "Digital deliverables attached to this listing. "
            "When present, ListBee delivers these to buyers on payment. "
            "Empty for listings where the seller handles delivery externally."
        ),
    )
    has_cover: bool = Field(
        description="`true` if a cover image exists (uploaded or auto-generated).",
        examples=[True],
    )
    checkout_schema: list[CheckoutFieldResponse] | None = Field(
        default=None,
        description="Custom fields collected from the buyer at checkout. Max 10.",
    )
    compare_at_price: int | None = Field(
        default=None,
        description="Strikethrough price in smallest currency unit.",
        examples=[3900],
    )
    badges: list[str] = Field(
        default_factory=list,
        description="Short promotional badges shown on the product page.",
        examples=[["Limited time", "Best seller"]],
    )
    cover_blur: BlurMode = Field(
        default=BlurMode.AUTO,
        description="Cover image blur mode. `true` always blurs, `false` never blurs, `auto` blurs image files.",
        examples=["auto"],
    )
    rating: float | None = Field(
        default=None,
        description="Seller-provided aggregate star rating (1–5).",
        examples=[4.8],
    )
    rating_count: int | None = Field(
        default=None,
        description="Seller-provided review or purchase count shown alongside the rating.",
        examples=[1243],
    )
    reviews: list[Review] = Field(
        default=[],
        description="Featured review cards shown on the product page.",
    )
    faqs: list[FaqItem] = Field(
        default=[],
        description="FAQ accordion items shown on the product page.",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Arbitrary key-value pairs forwarded in webhook events.",
        examples=[{"source": "n8n", "campaign": "launch-week"}],
    )
    utm_source: str | None = Field(
        default=None,
        description="UTM source tag attached to checkout links (e.g. 'twitter'). Null means use account defaults.",
        examples=["twitter"],
    )
    utm_medium: str | None = Field(
        default=None,
        description="UTM medium tag attached to checkout links (e.g. 'social'). Null means use account defaults.",
        examples=["social"],
    )
    utm_campaign: str | None = Field(
        default=None,
        description="UTM campaign tag attached to checkout links (e.g. 'launch-week'). Null means use account defaults.",
        examples=["launch-week"],
    )
    status: ListingStatus = Field(
        description="Current listing status.",
        examples=["draft"],
    )
    url: str | None = Field(
        default=None,
        description="Full product page URL — share this with buyers.",
        examples=["https://buy.listbee.so/seo-playbook"],
    )
    stock: int | None = Field(
        default=None,
        description="Available stock quantity. Null means unlimited.",
    )
    embed_url: str | None = Field(
        default=None,
        description="Embeddable checkout URL for this listing.",
    )
    readiness: ListingReadiness = Field(
        description=(
            "Monetization readiness. `sellable` is true when buyers can complete a purchase. "
            "If false, `actions` lists what's needed with resolve details and `next` points to the highest-priority action."
        ),
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the listing was created.",
    )

    @property
    def is_draft(self) -> bool:
        """True when the listing is in draft state (not visible to buyers)."""
        return self.status == "draft"

    @property
    def is_published(self) -> bool:
        """True when the listing is published and visible to buyers."""
        return self.status == "published"

    @property
    def is_in_stock(self) -> bool:
        """True when the listing has available stock (or unlimited stock when stock is None)."""
        return self.stock is None or self.stock > 0

    @property
    def checkout_url(self) -> str | None:
        """Full product page URL — share this with buyers. None if the listing is not published."""
        return self.url
