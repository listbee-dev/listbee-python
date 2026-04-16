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

    The ``api_key`` is returned **only once** — store it immediately in your secrets
    manager before making any other API calls.
    """

    object: Literal["bootstrap"] = Field(
        default="bootstrap",
        description="Object type identifier. Always `bootstrap`.",
        examples=["bootstrap"],
    )
    account_id: str = Field(
        description="Newly created account ID (acc_ prefixed).",
        examples=["acc_7kQ2xY9mN3pR5tW1"],
    )
    api_key: str = Field(
        description="Raw API key shown once at creation. Use as `Authorization: Bearer lb_...`.",
        examples=["lb_abc123"],
    )
