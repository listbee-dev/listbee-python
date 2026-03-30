"""Shared enums, readiness models, and StrEnum compatibility shim."""

from __future__ import annotations

import sys
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

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


class ActionKind(StrEnum):
    """Whether an action can be resolved by API call or requires human intervention."""

    API = "api"
    HUMAN = "human"


class ActionCode(StrEnum):
    """Machine-readable code identifying what action is needed."""

    SET_STRIPE_KEY = "set_stripe_key"
    CONNECT_STRIPE = "connect_stripe"
    ENABLE_CHARGES = "enable_charges"
    UPDATE_BILLING = "update_billing"


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
