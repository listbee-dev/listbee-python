"""Order response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from listbee.types.shared import FulfillmentStatus, OrderStatus, ShippingAddress


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
    fulfillment_status: FulfillmentStatus | None = Field(
        default=None,
        description="Fulfillment progress. Null for orders that don't require fulfillment tracking.",
        examples=["pending"],
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
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the order was created.",
    )
