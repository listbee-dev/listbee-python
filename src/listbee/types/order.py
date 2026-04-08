"""Order response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from listbee.types.shared import DeliverableResponse, OrderStatus


class OrderResponse(BaseModel):
    """Full order object returned by the ListBee API."""

    object: Literal["order"] = Field(
        default="order",
        description="Object type discriminator. Always `order`.",
        examples=["order"],
    )
    id: str = Field(
        description="Unique order identifier.",
        examples=["ord_9xM4kP7nR2qT5wY1"],
    )
    listing_id: str = Field(
        description="ID of the listing that was purchased.",
        examples=["lst_7kQ2xY9mN3pR5tW1vB8a"],
    )
    buyer_email: str = Field(
        description="Buyer's email address collected at checkout.",
        examples=["buyer@example.com"],
    )
    amount: int = Field(
        description="Amount paid in the smallest currency unit (e.g. 2900 = $29.00).",
        examples=[2900],
    )
    currency: str = Field(
        description="Three-letter ISO currency code, uppercase.",
        examples=["USD"],
    )
    stripe_payment_intent_id: str = Field(
        description="Stripe PaymentIntent associated with this payment.",
        examples=["pi_3abc123def456"],
    )
    status: OrderStatus = Field(
        description=(
            "Current order status. Full lifecycle: PENDING → PAID → PROCESSING (generated only) → FULFILLED. "
            "Terminal error states: CANCELED, FAILED. "
            "Use content_type to determine which statuses apply: "
            "static skips PROCESSING and auto-fulfills; "
            "generated enters PROCESSING until POST /fulfill is called; "
            "webhook stays PAID — delivery handled externally."
        ),
        examples=["paid"],
    )
    content_type: str = Field(
        description=(
            "Content type of the listing at the time of purchase. "
            "Determines the delivery model: "
            "static = ListBee auto-delivered pre-attached content on payment; "
            "generated = your system creates content after payment and pushes it via POST /fulfill; "
            "webhook = order.paid fired, your system handles delivery entirely."
        ),
        examples=["static"],
    )
    payment_status: str = Field(
        description=(
            "Stripe payment status, independent of order fulfillment status. "
            "Values: unpaid (payment not yet confirmed), paid (payment captured), "
            "refunded (full refund issued)."
        ),
        examples=["paid"],
    )
    checkout_data: dict[str, Any] | None = Field(
        default=None,
        description="Custom field values collected at checkout (from checkout_schema).",
    )
    listing_snapshot: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Immutable snapshot of listing data captured at payment time. "
            "Contains name, price, slug, and other listing fields as they existed when the buyer paid. "
            "Use this as the authoritative record of what was purchased — the listing may have changed since."
        ),
        examples=[{"name": "SEO Playbook 2026", "price": 2900, "slug": "seo-playbook-2026"}],
    )
    seller_snapshot: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Immutable snapshot of seller identity captured at payment time. "
            "Contains display_name and other account fields as they existed when the buyer paid. "
            "Useful for receipts and audit trails when account details change later."
        ),
        examples=[{"display_name": "Acme Agency", "email": "seller@example.com"}],
    )
    deliverables: list[DeliverableResponse] = Field(
        default=[],
        description="Deliverables attached to this order.",
    )
    paid_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when payment was confirmed.",
    )
    fulfilled_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the order was fulfilled.",
    )
    handed_off_at: datetime | None = Field(
        default=None,
        description=(
            "Timestamp when the order was handed off to the seller's external system via order.paid webhook. "
            "Only set for webhook content_type listings. Null for static and generated listings."
        ),
        examples=["2026-04-02T14:31:00Z"],
    )
    refund_amount: int = Field(
        default=0,
        description="Refund amount in smallest currency unit. 0 if not refunded.",
    )
    refunded_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the refund was issued.",
    )
    dispute_amount: int = Field(
        default=0,
        description="Disputed amount in smallest currency unit. 0 if not disputed.",
    )
    dispute_reason: str | None = Field(
        default=None,
        description="Reason for the dispute, if any.",
    )
    dispute_status: str | None = Field(
        default=None,
        description="Current dispute status (e.g. 'needs_response', 'won', 'lost').",
    )
    disputed_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the dispute was opened.",
    )
    platform_fee: int = Field(
        default=0,
        description="Platform fee in smallest currency unit collected by ListBee.",
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the order was created.",
    )

    @property
    def is_paid(self) -> bool:
        """True when payment has been captured."""
        return self.payment_status == "paid"

    @property
    def is_refunded(self) -> bool:
        """True when a full refund has been issued."""
        return self.payment_status == "refunded"

    @property
    def is_disputed(self) -> bool:
        """True when the order has an open dispute."""
        return self.dispute_status is not None

    @property
    def needs_fulfillment(self) -> bool:
        """True when the order is paid and awaiting generated content to be pushed via POST /fulfill."""
        return self.status == "paid" and self.content_type == "generated"

    @property
    def is_terminal(self) -> bool:
        """True when the order has reached a terminal state (fulfilled, handed_off, canceled, or failed)."""
        return self.status in ("fulfilled", "handed_off", "canceled", "failed")
