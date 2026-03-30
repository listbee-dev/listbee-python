"""Account response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import AccountReadiness


class AccountStats(BaseModel):
    """Aggregate statistics for an account."""

    total_revenue: int = Field(
        description="Total revenue in the smallest currency unit across all orders.",
        examples=[125000],
    )
    total_orders: int = Field(
        description="Total number of orders across all listings.",
        examples=[47],
    )
    total_listings: int = Field(
        description="Total number of listings on the account.",
        examples=[5],
    )


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
        description="Three-letter ISO currency code, uppercase. Set during onboarding.",
        examples=["USD"],
    )
    ga_measurement_id: str | None = Field(
        default=None,
        description="Google Analytics 4 Measurement ID (e.g. 'G-XXXXXXXXXX'). Used to track conversions on checkout pages.",
        examples=["G-XXXXXXXXXX"],
    )
    stats: AccountStats = Field(
        description="Aggregate statistics for this account.",
    )
    readiness: AccountReadiness = Field(
        description=(
            "Account operational readiness. `operational` is true when the account can sell. "
            "If false, `actions` lists what's needed with resolve details and `next` points to the highest-priority action."
        ),
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the account was created.",
    )
