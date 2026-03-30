"""Stripe response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class StripeConnectSessionResponse(BaseModel):
    """Stripe Connect onboarding session returned by the ListBee API."""

    model_config = ConfigDict(frozen=True)

    object: Literal["stripe_connect_session"]
    url: str
    expires_at: datetime
