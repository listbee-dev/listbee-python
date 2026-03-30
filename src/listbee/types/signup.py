"""Signup response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .account import AccountResponse


class SignupResponse(BaseModel):
    """Response from initiating a signup — confirms OTP was sent."""

    model_config = ConfigDict(frozen=True)

    object: Literal["signup_session"]
    email: str
    status: Literal["otp_sent"]
    message: str


class VerifyResponse(BaseModel):
    """Response from verifying a signup OTP — returns the new account and API key."""

    model_config = ConfigDict(frozen=True)

    object: Literal["signup_result"]
    account: AccountResponse
    api_key: str
