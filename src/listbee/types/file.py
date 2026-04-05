"""File response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """File object returned after upload. Token is valid for 24 hours."""

    object: Literal["file"] = Field(
        default="file",
        description="Object type discriminator. Always `file`.",
        examples=["file"],
    )
    id: str = Field(
        description="File token — pass to set_deliverables or deliver to attach.",
        examples=["file_7kQ2xY9mN3pR5tW1vB8a01"],
    )
    filename: str = Field(
        description="Original filename.",
        examples=["ebook.pdf"],
    )
    size: int = Field(
        description="File size in bytes.",
        examples=[2458631],
    )
    mime_type: str = Field(
        description="MIME type.",
        examples=["application/pdf"],
    )
    purpose: str = Field(
        description="File purpose: 'deliverable', 'cover', or 'avatar'.",
        examples=["deliverable"],
    )
    expires_at: datetime = Field(
        description="ISO 8601 timestamp when this token expires (24h after upload).",
    )
    created_at: datetime = Field(
        description="ISO 8601 timestamp of upload.",
    )
