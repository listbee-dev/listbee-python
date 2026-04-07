"""Auth/signup response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .account import AccountResponse


class OtpRequestResponse(BaseModel):
    """Response from sending an OTP — confirms the verification code was dispatched."""

    model_config = ConfigDict(frozen=True)

    object: Literal["otp_request"] = "otp_request"
    email: str
    expires_in: int = 300
    message: str = "Check your email for a 6-digit verification code."


class AuthSessionResponse(BaseModel):
    """Response from verifying an OTP — returns a short-lived access token and account details."""

    model_config = ConfigDict(frozen=True)

    object: Literal["auth_session"] = "auth_session"
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = 86400
    is_new: bool
    account: AccountResponse
