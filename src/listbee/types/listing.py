"""Listing response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import BlurMode, ContentType, ListingReadiness, ListingStatus


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
    currency: str = Field(
        description="Three-letter ISO currency code, uppercase.",
        examples=["USD"],
    )
    content_type: ContentType = Field(
        description="Auto-detected from the `content` value at creation.",
        examples=["file"],
    )
    has_content: bool = Field(
        description="`true` if content was successfully fetched and stored.",
        examples=[True],
    )
    has_cover: bool = Field(
        description="`true` if a cover image exists (uploaded or auto-generated).",
        examples=[True],
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
        default_factory=list,
        description="Featured review cards shown on the product page.",
        examples=[[]],
    )
    faqs: list[FaqItem] = Field(
        default_factory=list,
        description="FAQ accordion items shown on the product page.",
        examples=[[]],
    )
    metadata: dict | None = Field(
        default=None,
        description="Arbitrary key-value pairs forwarded in webhook events.",
        examples=[{"source": "n8n", "campaign": "launch-week"}],
    )
    status: ListingStatus = Field(
        description="Current listing publication status.",
        examples=["published"],
    )
    url: str | None = Field(
        default=None,
        description="Full product page URL — share this with buyers.",
        examples=["https://buy.listbee.so/seo-playbook"],
    )
    readiness: ListingReadiness = Field(
        description=(
            "Monetization readiness. `sellable` is true when buyers can complete a purchase. "
            "If false, `blockers` lists what's missing with machine-readable codes and resolve URLs."
        ),
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the listing was created.",
    )
