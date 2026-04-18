"""Event response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    """A single event from the ListBee event log.

    Events capture every significant state change on the account: orders paid,
    listings published, etc. Use the event log to reconcile missed webhook
    deliveries or audit order/listing history.
    """

    object: Literal["event"] = Field(
        default="event",
        description="Object type discriminator. Always `event`.",
        examples=["event"],
    )
    id: str = Field(
        description="Unique event identifier (evt_ prefixed).",
        examples=["evt_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )
    type: str = Field(
        description="Event type (e.g. 'order.paid', 'listing.published').",
        examples=["order.paid"],
    )
    account_id: str = Field(
        description="Account ID that owns this event.",
        examples=["acc_7kQ2xY9mN3pR5tW1"],
    )
    listing_id: str | None = Field(
        default=None,
        description="Listing ID associated with this event, if applicable.",
        examples=["lst_7kQ2xY9mN3pR5tW1vB8a"],
    )
    order_id: str | None = Field(
        default=None,
        description="Order ID associated with this event, if applicable.",
        examples=["ord_9xM4kP7nR2qT5wY1"],
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Event payload. Shape depends on event type.",
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when the event was created.",
    )
