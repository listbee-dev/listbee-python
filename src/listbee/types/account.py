"""Account response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import AccountReadiness


class AccountResponse(BaseModel):
    """Full account object returned by the ListBee API."""

    object: Literal["account"] = Field(
        default="account",
        description="Object type discriminator. Always `account`.",
        examples=["account"],
    )
    id: str = Field(
        description="Unique account identifier.",
        examples=["acc_7kQ2xY9mN3pR5tW1"],
    )
    email: str = Field(
        description="Account email address.",
        examples=["seller@example.com"],
    )
    plan: str = Field(
        description="Current plan tier.",
        examples=["free", "growth", "scale"],
    )
    fee_rate: str = Field(
        description="Transaction fee rate as a decimal string (e.g. '0.10' = 10%).",
        examples=["0.10", "0.05"],
    )
    currency: str | None = Field(
        default=None,
        description=(
            "Account currency (ISO 4217, lowercase). Set automatically from Stripe Connect. "
            "Cannot be changed after connection."
        ),
        examples=["usd", "eur"],
    )
    billing_status: str = Field(
        description="Current billing/subscription status.",
        examples=["active"],
    )
    ga_measurement_id: str | None = Field(
        default=None,
        description=(
            "Google Analytics 4 Measurement ID (e.g. 'G-XXXXXXXXXX'). Used to track conversions on checkout pages."
        ),
        examples=["G-XXXXXXXXXX"],
    )
    notify_orders: bool = Field(
        default=True,
        description="Whether the account receives email notifications for new orders.",
    )
    events_callback_url: str | None = Field(
        default=None,
        description=("Optional account-level webhook URL for non-order events. Set to null to remove."),
        examples=["https://agent.example.com/events"],
    )
    readiness: AccountReadiness = Field(
        description=(
            "Account operational readiness. `operational` is true when the account can sell. "
            "If false, `actions` lists what's needed with resolve details and `next` points to "
            "the highest-priority action."
        ),
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the account was created.",
    )
