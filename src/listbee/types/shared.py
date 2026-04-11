"""Shared enums, readiness models, and StrEnum compatibility shim."""

from __future__ import annotations

import sys
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):  # type: ignore[no-redef]
        """StrEnum backport for Python 3.10."""


class DeliverableType(StrEnum):
    """Type of digital deliverable attached to a listing."""

    FILE = "file"
    URL = "url"
    TEXT = "text"


class DeliverableStatus(StrEnum):
    """Status of a digital deliverable."""

    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class ActionPriority(StrEnum):
    """Priority level of a readiness action."""

    REQUIRED = "required"
    SUGGESTED = "suggested"


class PaymentStatus(StrEnum):
    """Stripe payment status, independent of order fulfillment status."""

    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


class CheckoutFieldType(StrEnum):
    """Supported field types for checkout schema fields."""

    TEXT = "text"
    SELECT = "select"
    DATE = "date"


class CheckoutFieldResponse(BaseModel):
    """A custom field collected from the buyer at checkout (response model)."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(
        description="Machine-readable field key (unique within the schema).",
        examples=["shirt_size"],
    )
    label: str = Field(
        description="Human-readable label shown to the buyer.",
        examples=["Shirt Size"],
    )
    type: CheckoutFieldType = Field(
        description="Field input type.",
        examples=["select"],
    )
    required: bool = Field(
        default=True,
        description="Whether the field must be filled before checkout completes.",
        examples=[True],
    )
    options: list[str] | None = Field(
        default=None,
        description="Available options when type is 'select'.",
        examples=[["S", "M", "L", "XL"]],
    )
    sort_order: int = Field(
        default=0,
        description="Display order. Lower values shown first.",
        examples=[0],
    )


class DeliverableResponse(BaseModel):
    """Digital deliverable attached to a listing or order."""

    model_config = ConfigDict(frozen=True)

    object: Literal["deliverable"] = Field(
        default="deliverable",
        description="Object type discriminator. Always `deliverable`.",
        examples=["deliverable"],
    )
    id: str = Field(
        description="Unique deliverable identifier (del_ prefixed).",
        examples=["del_7kQ2xY9mN3pR5tW1vB8a01"],
    )
    type: DeliverableType = Field(
        description="Type of deliverable: `file`, `url`, or `text`.",
        examples=["file"],
    )
    status: DeliverableStatus = Field(
        description="Deliverable status: `processing`, `ready`, or `failed`.",
        examples=["ready"],
    )
    content: str | None = Field(
        default=None,
        description="Text content (for text-type deliverables).",
    )
    filename: str | None = Field(
        default=None,
        description="Original filename (for file-type deliverables).",
        examples=["ebook.pdf"],
    )
    mime_type: str | None = Field(
        default=None,
        description="MIME type (for file-type deliverables).",
        examples=["application/pdf"],
    )
    size: int | None = Field(
        default=None,
        description="File size in bytes (for file-type deliverables).",
        examples=[2458631],
    )
    url: str | None = Field(
        default=None,
        description="URL (for url-type deliverables).",
    )


class BlurMode(StrEnum):
    """Cover image blur mode for a listing."""

    TRUE = "true"
    FALSE = "false"
    AUTO = "auto"


class ListingStatus(StrEnum):
    """Current publication status of a listing."""

    DRAFT = "draft"
    PUBLISHED = "published"


class OrderStatus(StrEnum):
    """Current status of an order."""

    PENDING = "pending"
    PAID = "paid"
    FULFILLED = "fulfilled"
    CANCELED = "canceled"
    FAILED = "failed"


class WebhookEventType(StrEnum):
    """Event types that can be subscribed to on a webhook endpoint."""

    ORDER_PAID = "order.paid"
    ORDER_FULFILLED = "order.fulfilled"
    ORDER_REFUNDED = "order.refunded"
    ORDER_DISPUTED = "order.disputed"
    ORDER_DISPUTE_CLOSED = "order.dispute_closed"
    ORDER_CANCELED = "order.canceled"
    LISTING_CREATED = "listing.created"
    LISTING_UPDATED = "listing.updated"
    LISTING_PUBLISHED = "listing.published"
    LISTING_OUT_OF_STOCK = "listing.out_of_stock"
    LISTING_DELETED = "listing.deleted"
    CUSTOMER_CREATED = "customer.created"


class ActionKind(StrEnum):
    """Whether an action can be resolved by API call or requires human intervention."""

    API = "api"
    HUMAN = "human"


class ActionCode(StrEnum):
    """Machine-readable code identifying what action is needed."""

    CONNECT_STRIPE = "connect_stripe"
    ENABLE_CHARGES = "enable_charges"
    UPDATE_BILLING = "update_billing"
    ATTACH_DELIVERABLE = "attach_deliverable"
    CONFIGURE_WEBHOOK = "configure_webhook"
    PUBLISH_LISTING = "publish_listing"
    WEBHOOK_DISABLED = "webhook_disabled"


class ActionResolve(BaseModel):
    """Resolution path for an action — either an API endpoint or a URL for human action."""

    model_config = ConfigDict(frozen=True)

    method: str = Field(
        description="HTTP method to resolve this action (e.g. PUT, POST, GET).",
        examples=["PUT"],
    )
    endpoint: str | None = Field(
        default=None,
        description="API endpoint to call when kind is 'api'.",
        examples=["/v1/account/stripe"],
    )
    url: str | None = Field(
        default=None,
        description="URL where the user can resolve this action when kind is 'human'.",
        examples=["https://dashboard.stripe.com/settings/charges"],
    )
    params: dict[str, Any] | None = Field(
        default=None,
        description="Parameters to include in the API call.",
    )


class Action(BaseModel):
    """A single action needed to reach readiness."""

    model_config = ConfigDict(frozen=True)

    code: ActionCode = Field(
        description="Machine-readable action identifier for automation branching.",
        examples=["set_stripe_key"],
    )
    kind: ActionKind = Field(
        description="Whether this action can be resolved via API or requires human intervention.",
        examples=["api"],
    )
    message: str = Field(
        description="Human-readable explanation. AI agents relay this to users.",
        examples=["Set your Stripe secret key via the API"],
    )
    resolve: ActionResolve = Field(
        description="Resolution path — API endpoint or human-facing URL.",
    )
    priority: ActionPriority = Field(
        default=ActionPriority.REQUIRED,
        description="Priority level: `required` blocks sellability, `suggested` is optional improvement.",
        examples=["required"],
    )


class ListingReadiness(BaseModel):
    """Monetization readiness state for a listing."""

    model_config = ConfigDict(frozen=True)

    sellable: bool = Field(
        description=(
            "True when buyers can complete a purchase on this listing. False means one or more actions are needed."
        ),
        examples=[True],
    )
    actions: list[Action] = Field(
        default=[],
        description="Actions needed to reach sellable state. Empty when `sellable` is true.",
    )
    next: str | None = Field(
        default=None,
        description="Code of the highest-priority action (prefers kind: api). Null when sellable.",
    )

    @property
    def is_ready(self) -> bool:
        """True when buyers can complete a purchase on this listing."""
        return self.sellable

    @property
    def next_action(self) -> Action | None:
        """Return the Action object for the highest-priority action, or None if ready."""
        if self.next is None:
            return None
        for action in self.actions:
            if action.code == self.next:
                return action
        return None

    def actions_by_kind(self, kind: str) -> list[Action]:
        """Return all actions of the given kind ('api' or 'human')."""
        return [a for a in self.actions if a.kind == kind]


class AccountReadiness(BaseModel):
    """Operational readiness state for an account."""

    model_config = ConfigDict(frozen=True)

    operational: bool = Field(
        description="True when the account can sell. False means one or more actions are needed.",
        examples=[True],
    )
    actions: list[Action] = Field(
        default=[],
        description="Actions needed to reach operational state. Empty when `operational` is true.",
    )
    next: str | None = Field(
        default=None,
        description="Code of the highest-priority action (prefers kind: api). Null when operational.",
    )

    @property
    def is_ready(self) -> bool:
        """True when the account can sell."""
        return self.operational

    @property
    def next_action(self) -> Action | None:
        """Return the Action object for the highest-priority action, or None if ready."""
        if self.next is None:
            return None
        for action in self.actions:
            if action.code == self.next:
                return action
        return None

    def actions_by_kind(self, kind: str) -> list[Action]:
        """Return all actions of the given kind ('api' or 'human')."""
        return [a for a in self.actions if a.kind == kind]


class WebhookReadiness(BaseModel):
    """Operational readiness state for a webhook endpoint."""

    model_config = ConfigDict(frozen=True)

    ready: bool = Field(
        description="True when the webhook can receive events.",
    )
    actions: list[Action] = Field(
        default=[],
        description="Actions needed to reach ready state.",
    )
    next: str | None = Field(
        default=None,
        description="Code of the highest-priority action.",
    )

    @property
    def is_ready(self) -> bool:
        """True when the webhook can receive events."""
        return self.ready

    @property
    def next_action(self) -> Action | None:
        """Return the Action object for the highest-priority action, or None if ready."""
        if self.next is None:
            return None
        for action in self.actions:
            if action.code == self.next:
                return action
        return None

    def actions_by_kind(self, kind: str) -> list[Action]:
        """Return all actions of the given kind ('api' or 'human')."""
        return [a for a in self.actions if a.kind == kind]


class OrderReadiness(BaseModel):
    """Fulfillment readiness state for an order."""

    model_config = ConfigDict(frozen=True)

    fulfilled: bool = Field(
        description="True when the order has been fulfilled. False means fulfillment is pending.",
        examples=[True],
    )
    actions: list[Action] = Field(
        default=[],
        description="Actions available or needed for this order (e.g. refund). Empty when fulfilled.",
    )
    next: str | None = Field(
        default=None,
        description="Code of the highest-priority action. Null when fulfilled.",
    )

    @property
    def is_ready(self) -> bool:
        """True when the order has been fulfilled."""
        return self.fulfilled

    @property
    def next_action(self) -> Action | None:
        """Return the Action object for the highest-priority action, or None if fulfilled."""
        if self.next is None:
            return None
        for action in self.actions:
            if action.code == self.next:
                return action
        return None

    def actions_by_kind(self, kind: str) -> list[Action]:
        """Return all actions of the given kind ('api' or 'human')."""
        return [a for a in self.actions if a.kind == kind]
