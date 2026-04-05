"""Customer response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CustomerResponse(BaseModel):
    """Customer object returned by the ListBee API.

    Customers are auto-created when a buyer completes their first order.
    They represent unique buyer email addresses.
    """

    object: Literal["customer"] = Field(
        default="customer",
        description="Object type discriminator. Always `customer`.",
        examples=["customer"],
    )
    id: str = Field(
        description="Unique customer identifier.",
        examples=["cus_7kQ2xY9mN3pR5tW1vB8a01"],
    )
    email: str = Field(
        description="Buyer email address.",
        examples=["alice@example.com"],
    )
    total_orders: int = Field(
        description="Total number of completed orders from this buyer.",
        examples=[3],
    )
    total_spent: int = Field(
        description="Total amount spent in the smallest currency unit.",
        examples=[8700],
    )
    currency: str = Field(
        description="Three-letter ISO currency code.",
        examples=["usd"],
    )
    first_order_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of the buyer's first purchase.",
    )
    last_order_at: datetime | None = Field(
        default=None,
        description="ISO 8601 timestamp of the buyer's most recent purchase.",
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of when this customer record was created.",
    )
