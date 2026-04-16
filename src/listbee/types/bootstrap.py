"""Bootstrap response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BootstrapResponse(BaseModel):
    """Response from POST /v1/bootstrap — step 1 of the bootstrap flow."""

    object: Literal["bootstrap_session"] = Field(
        default="bootstrap_session",
        description="Object type identifier.",
        examples=["bootstrap_session"],
    )
    session: str = Field(
        description="Bootstrap session ID. Pass to the next step.",
        examples=["sess_abc123"],
    )
    otp_sent: bool = Field(
        description="True when OTP was sent to the email address.",
        examples=[True],
    )


class BootstrapVerifyResponse(BaseModel):
    """Response from POST /v1/bootstrap/verify — step 2 of the bootstrap flow."""

    object: Literal["bootstrap_session"] = Field(
        default="bootstrap_session",
        description="Object type identifier.",
        examples=["bootstrap_session"],
    )
    verified: bool = Field(
        description="True when OTP was verified successfully.",
        examples=[True],
    )
    session: str = Field(
        description="Verified session ID. Pass to POST /v1/bootstrap/complete.",
        examples=["sess_abc123"],
    )


class BootstrapCompleteResponse(BaseModel):
    """Response from POST /v1/bootstrap/complete — step 3 of the bootstrap flow.

    The ``api_key`` is a one-time secret — store it immediately in your secrets
    manager. It is re-retrievable within 10 minutes by calling this endpoint again
    with the same session, after which it is permanently hidden.
    """

    object: Literal["bootstrap"] = Field(
        default="bootstrap",
        description="Object type identifier.",
        examples=["bootstrap"],
    )
    account_id: str = Field(
        description="Newly created or existing account ID. Use as the owner identity for all API calls.",
        examples=["acc_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )
    api_key: str = Field(
        description=(
            "One-time API key — store it immediately. "
            "Re-retrievable within 10 minutes by calling this endpoint again with the same session, "
            "after which it will NOT be shown again. "
            "Use as `Authorization: Bearer lb_...` on all subsequent API calls."
        ),
        examples=["lb_01J3K4M5N6P7Q8R9S0T1U2V3W4X5Y6Z7"],
    )
