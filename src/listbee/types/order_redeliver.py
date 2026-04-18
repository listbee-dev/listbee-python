"""Order redeliver response model."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RedeliveryAck(BaseModel):
    """Acknowledgement returned from POST /v1/orders/{id}/redeliver.

    Indicates that the ``order.paid`` and ``order.fulfilled`` events have been
    queued for re-delivery to the listing's ``agent_callback_url``.
    """

    object: Literal["redelivery_ack"] = Field(
        default="redelivery_ack",
        description="Object type discriminator. Always `redelivery_ack`.",
        examples=["redelivery_ack"],
    )
    order_id: str = Field(
        description="The order ID for which events were queued.",
        examples=["ord_9xM4kP7nR2qT5wY1"],
    )
    scheduled_attempts: int = Field(
        description="Number of webhook delivery attempts that were scheduled.",
        examples=[2],
    )
