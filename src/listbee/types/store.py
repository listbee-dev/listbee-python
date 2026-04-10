"""Store response models."""

from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.shared import Action as Action


class StoreReadiness(BaseModel):
    """Store readiness state."""

    sellable: bool = Field(
        description="True when the store can sell. False means actions are needed.",
        examples=[False],
    )
    actions: list[Action] = Field(  # pyright: ignore[reportUnknownVariableType]
        default_factory=list,
        description="What's needed to make this store sellable. Empty when sellable is true.",
    )
    next: str | None = Field(
        default=None,
        description="Code of the highest-priority action. Agents execute this first.",
        examples=["connect_stripe"],
    )


class StoreResponse(BaseModel):
    """Store object returned by the ListBee API."""

    object: Literal["store"] = Field(
        default="store",
        description="Object type identifier. Always `store`.",
        examples=["store"],
    )
    id: str = Field(
        description="Unique store ID (st_ prefixed).",
        examples=["st_7kQ2xY9mN3pR5tW1vB8a"],
    )
    display_name: str = Field(
        description="Store display name shown to buyers.",
        examples=["Acme Agency"],
    )
    slug: str = Field(
        description="URL-safe store slug used in checkout URLs.",
        examples=["acme-agency"],
    )
    bio: str | None = Field(
        default=None,
        description="Store bio shown on product pages.",
        examples=["We make great things."],
    )
    has_avatar: bool = Field(
        default=False,
        description="True when a store avatar has been uploaded.",
        examples=[False],
    )
    url: str = Field(
        description="Public store URL.",
        examples=["https://buy.listbee.so/acme-agency"],
    )
    api_key: str | None = Field(
        default=None,
        description="Raw API key, shown once at creation. Use as Bearer token.",
        examples=["lb_abc123"],
    )
    readiness: StoreReadiness = Field(
        description="Store readiness. Check `actions` for what's needed before you can sell.",
    )
