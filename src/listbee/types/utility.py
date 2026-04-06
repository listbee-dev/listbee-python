"""Utility response types."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    """Response from a ping request."""

    object: Literal["ping"] = Field(
        default="ping",
        description="Object type identifier.",
    )
    status: Literal["ok"] = Field(
        default="ok",
        description="API connectivity status.",
    )
