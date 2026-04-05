"""Order response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from listbee.types.shared import DeliverableResponse, OrderStatus, ShippingAddress


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
        description="Current order status.",
        examples=["paid"],
    )
    checkout_data: dict[str, Any] | None = Field(
        default=None,
        description="Custom field values collected at checkout (from checkout_schema).",
    )
    shipping_address: ShippingAddress | None = Field(
        default=None,
        description="Shipping address collected at checkout, if applicable.",
    )
    deliverables: list[DeliverableResponse] = Field(
        default=[],
        description="Deliverables attached to this order.",
    )
    shipped_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the order was marked as shipped.",
    )
    carrier: str | None = Field(
        default=None,
        description="Shipping carrier name (set via ship endpoint).",
        examples=["USPS"],
    )
    tracking_code: str | None = Field(
        default=None,
        description="Shipment tracking code (set via ship endpoint).",
        examples=["9400111899223456789012"],
    )
    seller_note: str | None = Field(
        default=None,
        description="Seller note to buyer (set via ship or fulfill endpoint).",
    )
    paid_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when payment was confirmed.",
    )
    fulfilled_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the order was fulfilled.",
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
