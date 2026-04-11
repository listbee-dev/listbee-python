"""Webhook response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import WebhookEventType, WebhookReadiness


class WebhookEventResponse(BaseModel):
    """Delivery event record for a webhook endpoint."""

    object: Literal["webhook_event"] = Field(
        default="webhook_event",
        description="Object type discriminator. Always `webhook_event`.",
        examples=["webhook_event"],
    )
    id: str = Field(description="Unique event identifier.", examples=["evt_7kQ2xY9mN3pR5tW1"])
    event_type: WebhookEventType = Field(
        description="The event type that triggered this delivery.", examples=["order.paid"]
    )
    status: Literal["pending", "delivered", "failed"] = Field(
        description="Computed delivery status.", examples=["delivered"]
    )
    attempts: int = Field(description="Number of delivery attempts made.", examples=[1])
    max_retries: int = Field(description="Maximum delivery attempts.", examples=[5])
    response_status: int | None = Field(default=None, description="HTTP status from last attempt.", examples=[200])
    last_error: str | None = Field(default=None, description="Error from last failed attempt.", examples=[None])
    created_at: datetime = Field(description="ISO 8601 timestamp of event creation.")
    delivered_at: datetime | None = Field(default=None, description="ISO 8601 timestamp of successful delivery.")
    failed_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the event delivery permanently failed.",
    )
    next_retry_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of the next scheduled retry. Null if delivered or failed.",
    )


class WebhookTestResponse(BaseModel):
    """Result of a test webhook delivery."""

    object: Literal["webhook_test"] = Field(
        default="webhook_test",
        description="Object type discriminator. Always `webhook_test`.",
        examples=["webhook_test"],
    )
    success: bool = Field(description="`true` if the endpoint returned a 2xx status code.", examples=[True])
    status_code: int | None = Field(default=None, description="HTTP status code from endpoint.", examples=[200])
    response_body: str | None = Field(
        default=None, description="Response body, truncated to 2000 chars.", examples=["OK"]
    )
    error: str | None = Field(default=None, description="Error message if delivery failed.", examples=[None])


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
        examples=[["order.paid"]],
    )
    enabled: bool = Field(
        description="`false` when delivery is paused without deleting the endpoint.",
        examples=[True],
    )
    disabled_reason: str | None = Field(
        default=None,
        description="Reason the webhook was automatically disabled, if applicable.",
    )
    readiness: WebhookReadiness = Field(
        description="Delivery readiness. `ready` is true when events can be sent.",
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the webhook endpoint was created.",
    )


class WebhookListResponse(BaseModel):
    """List of webhook endpoints."""

    object: Literal["list"] = Field(
        default="list",
        description="Object type discriminator. Always `list`.",
        examples=["list"],
    )
    data: list[WebhookResponse] = Field(
        description="Array of webhook objects.",
    )
    cursor: str | None = Field(
        default=None,
        description="Pass as `cursor` query param to fetch the next page.",
        examples=["wh_3mK8nP2qR5tW7xY1"],
    )
    has_more: bool = Field(
        default=False,
        description="True if more results exist beyond this page.",
        examples=[False],
    )
