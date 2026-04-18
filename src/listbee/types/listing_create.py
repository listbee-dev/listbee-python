"""Listing create and signing-secret response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from listbee.types.listing import ListingBase, ListingDetailResponse


class ListingCreateResponse(BaseModel):
    """Response from POST /v1/listings.

    Contains the created :class:`ListingBase` plus a one-time ``signing_secret`` reveal.
    Store the secret immediately — it will not be shown again in full.

    The ``object`` discriminator is ``"listing_with_secret"`` so you can distinguish this
    envelope from a plain listing object.
    """

    object: Literal["listing_with_secret"] = Field(
        default="listing_with_secret",
        description="Object type discriminator. Always `listing_with_secret` — signals that `signing_secret` is present.",
        examples=["listing_with_secret"],
    )
    signing_secret: str = Field(
        description=(
            "HMAC-SHA256 signing secret for verifying webhook payloads from this listing. "
            "Returned ONCE at creation — not exposed on subsequent reads. "
            "Store it immediately. To rotate, call PUT /v1/listings/{id} with a new `signing_secret` value."
        ),
        examples=["my-long-signing-secret-value"],
    )
    listing: ListingBase = Field(
        description="The newly created listing object.",
    )


class RotateSigningSecretResponse(BaseModel):
    """Response from PUT /v1/listings/{id} when ``signing_secret`` is rotated.

    Contains the updated :class:`ListingDetailResponse` plus the new one-time ``signing_secret``.
    Store the new secret immediately.
    """

    object: Literal["rotate_signing_secret"] = Field(
        default="rotate_signing_secret",
        description="Object type discriminator. Always `rotate_signing_secret`.",
        examples=["rotate_signing_secret"],
    )
    listing: ListingDetailResponse = Field(
        description="The updated listing.",
    )
    signing_secret: str = Field(
        description=(
            "New signing secret. Replaces the previous one immediately. "
            "Store immediately — only shown once."
        ),
        examples=["new-long-signing-secret-value"],
    )
