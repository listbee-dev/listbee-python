"""Plan response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PlanResponse(BaseModel):
    """A pricing plan offered by ListBee."""

    object: Literal["plan"] = Field(
        default="plan",
        description="Object type discriminator. Always `plan`.",
        examples=["plan"],
    )
    id: str = Field(
        description="Plan identifier",
        examples=["free"],
    )
    name: str = Field(
        description="Display name",
        examples=["Free"],
    )
    tagline: str = Field(
        description="Short description",
        examples=["Start instantly"],
    )
    price_monthly: int = Field(
        description="Monthly price in USD",
        examples=[0],
    )
    fee_rate: str = Field(
        description="Platform fee rate as decimal string",
        examples=["0.10"],
    )


class PlanListResponse(BaseModel):
    """List of pricing plans."""

    object: Literal["list"] = Field(
        default="list",
        description="Object type discriminator. Always `list`.",
        examples=["list"],
    )
    data: list[PlanResponse] = Field(
        description="Array of plan objects.",
    )
    cursor: str | None = Field(
        default=None,
        description="Pass as `cursor` query param to fetch the next page.",
        examples=[None],
    )
    has_more: bool = Field(
        default=False,
        description="True if more results exist beyond this page.",
        examples=[False],
    )
