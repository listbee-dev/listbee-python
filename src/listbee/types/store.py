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
