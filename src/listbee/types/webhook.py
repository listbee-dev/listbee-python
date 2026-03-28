"""Webhook response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import WebhookEventType


class WebhookResponse(BaseModel):
    """Full webhook endpoint object returned by the ListBee API."""

    object: Literal["webhook"] = Field(
        default="webhook",
        description="Object type discriminator. Always `webhook`.",
        examples=["webhook"],
    )
    id: str = Field(
        description="Unique webhook identifier.",
        examples=["wh_3mK8nP2qR5tW7xY1"],
    )
    name: str = Field(
        description="Display name for identifying this endpoint.",
        examples=["Order notifications"],
    )
    url: str = Field(
        description="HTTPS endpoint URL that receives POST requests for each event.",
        examples=["https://example.com/webhooks/listbee"],
    )
    secret: str = Field(
        description="HMAC signing secret — use this to verify payload signatures.",
        examples=["whsec_a1b2c3d4e5f6"],
    )
    events: list[WebhookEventType] = Field(
        description="Subscribed event types. An empty list means all events are delivered.",
        examples=[["order.completed"]],
    )
    enabled: bool = Field(
        description="`false` when delivery is paused without deleting the endpoint.",
        examples=[True],
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the webhook endpoint was created.",
    )
