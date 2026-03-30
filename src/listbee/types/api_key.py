"""API key response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ApiKeyResponse(BaseModel):
    """API key object returned by the ListBee API."""

    model_config = ConfigDict(frozen=True)

    object: Literal["api_key"]
    id: str
    name: str
    prefix: str
    key: str | None = None
    created_at: datetime
