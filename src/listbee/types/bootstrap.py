"""Bootstrap response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import AccountReadiness


class BootstrapStartResponse(BaseModel):
    """Response from POST /v1/bootstrap/start — step 1 of the bootstrap flow.

    Contains a ``bootstrap_token`` to pass to :meth:`~listbee.resources.bootstrap.Bootstrap.verify`
    and an ``account_id`` that identifies the account being bootstrapped.
    """

    object: Literal["bootstrap_session"] = Field(
        default="bootstrap_session",
        description="Object type identifier.",
        examples=["bootstrap_session"],
    )
    bootstrap_token: str = Field(
        description="Bootstrap token. Pass to POST /v1/bootstrap/verify along with the OTP.",
        examples=["bst_abc123def456"],
    )
    account_id: str = Field(
        description="Account ID being bootstrapped. Use with bootstrap.poll() to check readiness.",
        examples=["acc_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )
    otp_expires_at: str = Field(
        description="ISO 8601 timestamp when the OTP expires.",
        examples=["2026-04-18T12:10:00Z"],
    )


# Backwards-compatible alias — kept so existing code doesn't break immediately
BootstrapResponse = BootstrapStartResponse


class BootstrapVerifyResponse(BaseModel):
    """Response from POST /v1/bootstrap/verify — step 2 of the bootstrap flow.

    The ``api_key`` is a one-time secret — store it immediately.
    ``stripe_onboarding_url`` is where the user must go to connect Stripe
    (required before selling). ``readiness`` shows the account's current state.
    """

    object: Literal["bootstrap"] = Field(
        default="bootstrap",
        description="Object type identifier.",
        examples=["bootstrap"],
    )
    account_id: str = Field(
        description="Account ID. Use as the owner identity for all API calls.",
        examples=["acc_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )
    api_key: str = Field(
        description=(
            "One-time API key — store it immediately. "
            "Use as `Authorization: Bearer lb_...` on all subsequent API calls."
        ),
        examples=["lb_01J3K4M5N6P7Q8R9S0T1U2V3W4X5Y6Z7"],
    )
    stripe_onboarding_url: str | None = Field(
        default=None,
        description=(
            "Stripe Connect onboarding URL. Present when Stripe is not yet connected. "
            "Show this to the user — they must complete onboarding before selling."
        ),
        examples=["https://connect.stripe.com/setup/e/acct_..."],
    )
    readiness: AccountReadiness = Field(
        description="Account operational readiness after bootstrap.",
    )


class BootstrapPollResponse(BaseModel):
    """Response from GET /v1/bootstrap/{account_id} — poll readiness after OTP verify.

    Poll until ``ready`` is ``True`` to confirm the account is operational.
    """

    object: Literal["bootstrap_poll"] = Field(
        default="bootstrap_poll",
        description="Object type identifier.",
        examples=["bootstrap_poll"],
    )
    ready: bool = Field(
        description="True when the account is fully operational and ready to sell.",
        examples=[False],
    )
    account_id: str = Field(
        description="Account ID being polled.",
        examples=["acc_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )
    readiness: AccountReadiness = Field(
        description="Full readiness state including pending actions.",
    )
    stripe_onboarding_url: str | None = Field(
        default=None,
        description=(
            "Stripe Connect onboarding URL — present when Stripe is not yet connected. "
            "Show this URL to the user so they can complete onboarding."
        ),
        examples=["https://connect.stripe.com/setup/e/acct_..."],
    )


# Legacy aliases — kept for backwards compatibility during migration
BootstrapCompleteResponse = BootstrapVerifyResponse
