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
        description="Verified session ID. Pass to POST /v1/bootstrap/store.",
        examples=["sess_abc123"],
    )
