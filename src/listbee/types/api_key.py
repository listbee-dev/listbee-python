"""API key response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ApiKeyResponse(BaseModel):
    """API key object returned after self-revoke."""

    object: Literal["api_key"] = Field(
        default="api_key",
        description="Object type discriminator. Always `api_key`.",
        examples=["api_key"],
    )
    id: str = Field(
        description="Unique API key entity identifier (lbk_ prefixed).",
        examples=["lbk_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )
    name: str = Field(
        description="Human-readable name for this key.",
        examples=["default"],
    )
    prefix: str = Field(
        description="First few characters of the key for identification.",
        examples=["lb_abc1"],
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the key was created.",
    )
    last_used_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of the last successful use.",
    )
    revoked_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the key was revoked. Set after self_revoke().",
    )
