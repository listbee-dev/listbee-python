"""Listing create response model (one-time signing_secret reveal)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.listing import ListingResponse


class CreateListingResponse(BaseModel):
    """Response from POST /v1/listings.

    Contains the created listing plus a one-time ``signing_secret`` reveal.
    Store the secret immediately — it will not be shown again in full
    (only the last 4 chars preview is available via ``listing.signing_secret_preview``).
    """

    object: Literal["listing_create"] = Field(
        default="listing_create",
        description="Object type discriminator. Always `listing_create`.",
        examples=["listing_create"],
    )
    listing: ListingResponse = Field(
        description="The newly created listing.",
    )
    signing_secret: str = Field(
        description=(
            "One-time signing secret for this listing. "
            "Used to verify webhook payloads from `agent_callback_url`. "
            "Store immediately — only the last 4 chars are shown again via `signing_secret_preview`."
        ),
        examples=["lbs_sk_01J3K4M5N6P7Q8R9S0T1U2V3W4"],
    )


class RotateSigningSecretResponse(BaseModel):
    """Response from PATCH /v1/listings/{id} when signing_secret is rotated.

    Contains the updated listing plus the new one-time ``signing_secret``.
    Store the new secret immediately.
    """

    object: Literal["rotate_signing_secret"] = Field(
        default="rotate_signing_secret",
        description="Object type discriminator. Always `rotate_signing_secret`.",
        examples=["rotate_signing_secret"],
    )
    listing: ListingResponse = Field(
        description="The updated listing with new signing_secret_preview.",
    )
    signing_secret: str = Field(
        description=(
            "New signing secret. Replaces the previous one immediately. "
            "Store immediately — only the last 4 chars are shown again."
        ),
        examples=["lbs_sk_new9K4M5N6P7Q8R9S0T1U2V3W4"],
    )
