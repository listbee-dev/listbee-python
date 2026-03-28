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
    readiness: AccountReadiness = Field(
        description=(
            "Account operational readiness. `operational` is true when the account can sell. "
            "If false, `blockers` lists what's missing with resolve URLs."
        ),
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the account was created.",
    )
