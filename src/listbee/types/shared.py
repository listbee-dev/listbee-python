"""Shared enums, readiness models, and StrEnum compatibility shim."""

from __future__ import annotations

import sys
from enum import Enum

from pydantic import BaseModel, Field

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):  # type: ignore[no-redef]
        """StrEnum backport for Python 3.10."""


class ContentType(StrEnum):
    """Auto-detected content type of a listing's digital content."""

    FILE = "file"
    URL = "url"
    TEXT = "text"


class BlurMode(StrEnum):
    """Cover image blur mode for a listing."""

    TRUE = "true"
    FALSE = "false"
    AUTO = "auto"


class ListingStatus(StrEnum):
    """Current publication status of a listing."""

    PUBLISHED = "published"


class OrderStatus(StrEnum):
    """Current fulfillment status of an order."""

    COMPLETED = "completed"


class WebhookEventType(StrEnum):
    """Event types that can be subscribed to on a webhook endpoint."""

    ORDER_COMPLETED = "order.completed"
    ORDER_REFUNDED = "order.refunded"
    ORDER_DISPUTED = "order.disputed"
    ORDER_DISPUTE_CLOSED = "order.dispute_closed"
    LISTING_CREATED = "listing.created"


class BlockerCode(StrEnum):
    """Machine-readable code identifying what is blocking sales or operations."""

    PAYMENTS_NOT_CONFIGURED = "payments_not_configured"
    CHARGES_DISABLED = "charges_disabled"
    BILLING_PAST_DUE = "billing_past_due"
    BILLING_UNPAID = "billing_unpaid"


class BlockerAction(StrEnum):
    """Machine-readable action to resolve a blocker."""

    CONNECT_STRIPE = "connect_stripe"
    ENABLE_CHARGES = "enable_charges"
    UPDATE_BILLING = "update_billing"


class BlockerResolve(BaseModel):
    """Action and URL required to resolve a specific blocker."""

    action: BlockerAction = Field(
        description="Machine-readable action identifier.",
        examples=["connect_stripe"],
    )
    url: str = Field(
        description="URL where the user can resolve this blocker.",
        examples=["https://listbee.so/console/connect/stripe"],
    )


class Blocker(BaseModel):
    """A single condition that is preventing sales or account operations."""

    code: BlockerCode = Field(
        description="Machine-readable blocker identifier for automation branching.",
        examples=["payments_not_configured"],
    )
    message: str = Field(
        description="Human-readable explanation. AI agents relay this to users.",
        examples=["Connect a Stripe account to accept payments on this listing"],
    )
    resolve: BlockerResolve = Field(
        description="Action and URL to resolve this blocker.",
    )


class ListingReadiness(BaseModel):
    """Monetization readiness state for a listing."""

    sellable: bool = Field(
        description=(
            "True when buyers can complete a purchase on this listing. False means one or more blockers prevent sales."
        ),
        examples=[True],
    )
    blockers: list[Blocker] = Field(
        default_factory=list,
        description="What's preventing sales. Empty when `sellable` is true.",
        examples=[[]],
    )


class AccountReadiness(BaseModel):
    """Operational readiness state for an account."""

    operational: bool = Field(
        description=("True when the account can sell. False means one or more blockers prevent operations."),
        examples=[True],
    )
    blockers: list[Blocker] = Field(
        default_factory=list,
        description="What's preventing operations. Empty when `operational` is true.",
        examples=[[]],
    )
