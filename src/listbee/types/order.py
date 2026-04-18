"""Order response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from listbee.types.shared import Action, DeliverableResponse, OrderReadiness, OrderStatus


class OrderSummary(BaseModel):
    """Slim order object returned in list responses.

    Use :meth:`~listbee.resources.orders.Orders.get` to retrieve the full
    :class:`OrderResponse` with checkout data, snapshots, deliverable, and all other fields.
    """

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
    status: OrderStatus = Field(
        description="Current order status. Lifecycle: PAID → FULFILLED.",
        examples=["paid"],
    )
    has_deliverables: bool = Field(
        default=False,
        description="`true` if auto-fulfilled by ListBee via static deliverable.",
        examples=[False],
    )
    payment_status: str = Field(
        description=(
            "Stripe payment status, independent of order fulfillment status. "
            "Values: unpaid (payment not yet confirmed), paid (payment captured), "
            "refunded (full refund issued)."
        ),
        examples=["paid"],
    )
    platform_fee: int = Field(
        default=0,
        description="Platform fee in smallest currency unit collected by ListBee.",
    )
    refund_amount: int = Field(
        default=0,
        description="Refund amount in smallest currency unit. 0 if not refunded.",
    )
    dispute_status: str | None = Field(
        default=None,
        description="Current dispute status (e.g. 'needs_response', 'won', 'lost').",
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
        description="Current order status. Lifecycle: PENDING → PAID → FULFILLED.",
        examples=["paid"],
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
            "Use this as the authoritative record of what was purchased."
        ),
        examples=[{"name": "SEO Playbook 2026", "price": 2900, "slug": "seo-playbook-2026"}],
    )
    seller_snapshot: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Immutable snapshot of seller identity captured at payment time. "
            "Contains display_name and other account fields as they existed when the buyer paid."
        ),
        examples=[{"display_name": "Acme Agency", "email": "seller@example.com"}],
    )
    has_deliverables: bool = Field(
        default=False,
        description="`true` if a deliverable is attached to this order.",
        examples=[False],
    )
    deliverable: DeliverableResponse | None = Field(
        default=None,
        description=(
            "Single digital deliverable attached to this order after fulfillment. "
            "Null for external-fulfillment orders or before fulfillment."
        ),
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Arbitrary key-value pairs attached to this order. "
            "Stripe-aligned limits: max 50 keys, keys ≤ 40 chars, string values ≤ 500 chars."
        ),
        examples=[{"generated_by": "my-agent", "version": "1"}],
    )
    unlock_url: str | None = Field(
        default=None,
        description=("Permanent bearer link sent to the buyer. The buyer uses this to access their purchased content."),
        examples=["https://buy.listbee.so/dl/ord_9xM4kP7nR2qT5wY1?token=..."],
    )
    actions: list[Action] | None = Field(
        default=None,
        description=(
            "Actions available for this order (e.g. fulfill, refund). "
            "Each action has a `priority` field indicating whether it is `required` or `suggested`."
        ),
    )
    readiness: OrderReadiness | None = Field(
        default=None,
        description="Fulfillment readiness state for this order. Includes available actions and next priority.",
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
        """True when the order is paid and has not yet been fulfilled."""
        return self.status == "paid"

    @property
    def is_terminal(self) -> bool:
        """True when the order has reached a terminal state (fulfilled)."""
        return self.status == "fulfilled"
