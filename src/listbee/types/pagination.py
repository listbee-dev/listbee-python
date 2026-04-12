"""Pagination response models."""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class CursorPage(BaseModel, Generic[T]):
    """Cursor-paginated list response wrapping any object type.

    Use `has_more` and `cursor` to iterate through pages.
    Pass `cursor` as the `cursor` query parameter on the next request.
    """

    object: Literal["list"] = Field(
        default="list",
        description="Object type discriminator. Always `list`.",
        examples=["list"],
    )
    data: list[T] = Field(
        description="Array of objects on this page.",
        examples=[[]],
    )
    has_more: bool = Field(
        description="`true` if more results exist beyond this page.",
        examples=[False],
    )
    cursor: str | None = Field(
        default=None,
        description="Pass as the `cursor` query parameter to fetch the next page. `null` on the last page.",
        examples=[None],
    )
