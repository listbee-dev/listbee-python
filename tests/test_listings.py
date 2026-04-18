"""Tests for the Listings resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.deliverable import Deliverable
from listbee.resources.listings import Listings
from listbee.types.listing import ListingBase, ListingDetailResponse, ListingSummary
from listbee.types.listing_create import ListingCreateResponse, RotateSigningSecretResponse

# Minimal readiness object (buyable = true)
_READINESS = {"buyable": True, "actions": [], "next": None}

# Minimal stats object
_STATS = {"schema_version": 1, "views": 0, "purchases": 0, "gmv_minor": 0}

# Base ListingBase fixture — shape returned inside ListingCreateResponse.listing
LISTING_BASE_JSON = {
    "object": "listing",
    "id": "lst_abc123",
    "url": "https://buy.listbee.so/l/lst_abc123/seo-playbook",
    "name": "SEO Playbook",
    "price": 2900,
    "currency": "usd",
    "status": "published",
    "fulfillment_mode": "MANAGED",
    "image_url": None,
    "agent_callback_url": None,
    "deliverable": {
        "type": "url",
        "content": "https://example.com/ebook",
    },
    "readiness": _READINESS,
    "checkout_schema": None,
    "metadata": None,
    "tagline": None,
    "description": None,
    "highlights": [],
    "faqs": [],
    "cta": None,
    "compare_at_price": None,
    "badges": [],
    "rating": None,
    "rating_count": None,
    "reviews": [],
    "created_at": "2026-03-30T12:00:00Z",
}

# ListingCreateResponse envelope — POST /v1/listings
CREATE_RESPONSE_JSON = {
    "object": "listing_with_secret",
    "signing_secret": "lbs_sk_abc123secretvalue",
    "listing": LISTING_BASE_JSON,
}

# ListingDetailResponse — GET/PUT /v1/listings/{id}
LISTING_DETAIL_JSON = {
    **LISTING_BASE_JSON,
    "stats": _STATS,
}

# Async-mode listing inside detail response
ASYNC_LISTING_DETAIL_JSON = {
    **LISTING_DETAIL_JSON,
    "id": "lst_ext456",
    "url": "https://buy.listbee.so/l/lst_ext456/custom-service",
    "name": "Custom Service",
    "fulfillment_mode": "ASYNC",
    "deliverable": None,
    "agent_callback_url": "https://yourapp.com/webhooks/listbee",
    "checkout_schema": [
        {
            "key": "shirt_size",
            "label": "Shirt Size",
            "type": "select",
            "required": True,
            "options": ["S", "M", "L", "XL"],
            "sort_order": 0,
        }
    ],
}

LISTING_SUMMARY_JSON = {
    "object": "listing",
    "id": "lst_abc123",
    "url": "https://buy.listbee.so/l/lst_abc123/seo-playbook",
    "name": "SEO Playbook",
    "tagline": None,
    "price": 2900,
    "currency": "usd",
    "compare_at_price": None,
    "cta": None,
    "badges": [],
    "highlights": [],
    "status": "published",
    "fulfillment_mode": "MANAGED",
    "image_url": None,
    "created_at": "2026-03-30T12:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def listings(sync_client):
    return Listings(sync_client)


class TestCreateListing:
    def test_create_listing_returns_listing_create_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            result = listings.create(name="SEO Playbook", price=2999)
        assert isinstance(result, ListingCreateResponse)
        assert result.object == "listing_with_secret"
        assert result.signing_secret == "lbs_sk_abc123secretvalue"
        assert isinstance(result.listing, ListingBase)
        assert result.listing.id == "lst_abc123"
        assert result.listing.name == "SEO Playbook"
        assert result.listing.price == 2900
        assert result.listing.currency == "usd"
        assert result.listing.status == "published"
        assert result.listing.fulfillment_mode == "MANAGED"

    def test_create_listing_envelope_contains_listing_base(self, listings):
        """POST /v1/listings returns ListingCreateResponse (envelope), not a flat listing."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            result = listings.create(name="SEO Playbook", price=2999)
        # listing is a ListingBase, not a ListingDetailResponse (no stats)
        assert not isinstance(result.listing, ListingDetailResponse)
        assert isinstance(result.listing, ListingBase)

    def test_create_listing_with_deliverable_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(
                name="Test",
                price=100,
                deliverable=Deliverable.url("https://example.com/secret"),
            )
        body = json.loads(route.calls[0].request.content)
        # deliverable uses "content" key (not "value")
        assert body["deliverable"] == {"type": "url", "content": "https://example.com/secret"}

    def test_create_listing_with_text_deliverable(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(
                name="Test",
                price=100,
                deliverable=Deliverable.text("License: ABCD-1234"),
            )
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == {"type": "text", "content": "License: ABCD-1234"}

    def test_create_listing_with_image_url_and_currency(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(
                name="Test",
                price=100,
                image_url="https://cdn.example.com/cover.jpg",
                currency="eur",
            )
        body = json.loads(route.calls[0].request.content)
        assert body["image_url"] == "https://cdn.example.com/cover.jpg"
        assert body["currency"] == "eur"

    def test_create_listing_with_readiness_actions(self, listings):
        create_with_blockers = {
            **CREATE_RESPONSE_JSON,
            "listing": {
                **LISTING_BASE_JSON,
                "readiness": {
                    "buyable": False,
                    "actions": [
                        {
                            "code": "stripe_connect_required",
                            "kind": "api",
                            "message": "Connect your Stripe account via the API",
                            "resolve": {
                                "method": "POST",
                                "endpoint": "/v1/account/stripe-connect-session",
                                "url": None,
                                "params": {"return_url": "https://example.com"},
                            },
                        }
                    ],
                    "next": "stripe_connect_required",
                },
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=create_with_blockers))
            result = listings.create(name="SEO Playbook", price=2999)
        assert result.listing.readiness.buyable is False
        assert len(result.listing.readiness.actions) == 1
        assert result.listing.readiness.actions[0].code == "stripe_connect_required"
        assert result.listing.readiness.actions[0].kind == "api"
        assert result.listing.readiness.actions[0].resolve.endpoint == "/v1/account/stripe-connect-session"
        assert result.listing.readiness.next == "stripe_connect_required"

    def test_create_listing_optional_fields_omitted_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(name="SEO Playbook", price=2999)
        body = json.loads(route.calls[0].request.content)
        assert "description" not in body
        assert "tagline" not in body
        assert "cover_blur" not in body
        assert "deliverable" not in body
        assert "utm_source" not in body
        assert "utm_medium" not in body
        assert "utm_campaign" not in body
        assert "fulfillment_mode" not in body

    def test_create_listing_with_checkout_schema(self, listings):
        schema = [{"key": "shirt_size", "label": "Shirt Size", "type": "select", "options": ["S", "M", "L"]}]
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(name="T-Shirt", price=2500, checkout_schema=schema)
        body = json.loads(route.calls[0].request.content)
        assert body["checkout_schema"] == schema

    def test_create_listing_with_checkout_field_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            from listbee.checkout_field import CheckoutField

            listings.create(
                name="Sneakers",
                price=8500,
                checkout_schema=[
                    CheckoutField.select("size", label="Size", options=["S", "M", "L"], sort_order=0),
                    CheckoutField.text("notes", label="Notes", required=False, sort_order=1),
                ],
            )
            body = json.loads(route.calls[0].request.content)
            assert body["checkout_schema"] == [
                {
                    "key": "size",
                    "type": "select",
                    "label": "Size",
                    "options": ["S", "M", "L"],
                    "required": True,
                    "sort_order": 0,
                },
                {"key": "notes", "type": "text", "label": "Notes", "required": False, "sort_order": 1},
            ]

    def test_create_listing_with_signing_secret(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(name="Test", price=100, signing_secret="my_secret")
        body = json.loads(route.calls[0].request.content)
        assert body["signing_secret"] == "my_secret"


class TestGetListing:
    def test_get_listing_by_id(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert isinstance(result, ListingDetailResponse)
        assert result.id == "lst_abc123"
        assert result.currency == "usd"

    def test_get_listing_sends_correct_path(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            listings.get("lst_abc123")
        assert route.called

    def test_get_listing_includes_stats(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert result.stats.views == 0
        assert result.stats.purchases == 0
        assert result.stats.gmv_minor == 0

    def test_listing_response_has_single_deliverable(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert result.deliverable is not None
        assert result.deliverable.type == "url"
        assert result.deliverable.content == "https://example.com/ebook"

    def test_listing_response_has_buyable_readiness(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert result.readiness.buyable is True
        assert result.readiness.is_ready is True

    def test_listing_response_has_composite_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert "/l/" in result.url

    def test_listing_response_async_mode(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_ext456").mock(return_value=httpx.Response(200, json=ASYNC_LISTING_DETAIL_JSON))
            result = listings.get("lst_ext456")
        assert result.fulfillment_mode == "ASYNC"
        assert result.agent_callback_url == "https://yourapp.com/webhooks/listbee"
        assert result.deliverable is None
        assert result.checkout_schema is not None
        assert len(result.checkout_schema) == 1
        assert result.checkout_schema[0].key == "shirt_size"
        assert result.checkout_schema[0].type == "select"
        assert result.checkout_schema[0].options == ["S", "M", "L", "XL"]
        assert result.checkout_schema[0].sort_order == 0

    def test_listing_response_has_no_old_fields(self, listings):
        """Verify removed fields are not present on ListingDetailResponse."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert not hasattr(result, "fulfillment_url")
        assert not hasattr(result, "has_deliverables")
        assert not hasattr(result, "stock")
        assert not hasattr(result, "deliverables")
        assert not hasattr(result, "short_code")
        assert not hasattr(result, "has_cover")
        assert not hasattr(result, "cover_blur")
        assert not hasattr(result, "signing_secret_preview")
        assert not hasattr(result, "embed_url")


class TestListListings:
    def test_list_returns_cursor_page(self, listings):
        list_json = {
            "object": "list",
            "data": [LISTING_SUMMARY_JSON],
            "has_more": False,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=list_json))
            page = listings.list()
        assert len(page.data) == 1
        assert isinstance(page.data[0], ListingSummary)
        assert page.data[0].id == "lst_abc123"
        assert page.data[0].currency == "usd"

    def test_list_summary_has_image_url(self, listings):
        summary_with_image = {**LISTING_SUMMARY_JSON, "image_url": "https://cdn.example.com/cover.jpg"}
        list_json = {"object": "list", "data": [summary_with_image], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=list_json))
            page = listings.list()
        assert page.data[0].image_url == "https://cdn.example.com/cover.jpg"

    def test_list_summary_has_fulfillment_mode(self, listings):
        list_json = {
            "object": "list",
            "data": [LISTING_SUMMARY_JSON],
            "has_more": False,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=list_json))
            page = listings.list()
        assert page.data[0].fulfillment_mode == "MANAGED"

    def test_list_summary_has_no_old_fields(self, listings):
        list_json = {
            "object": "list",
            "data": [LISTING_SUMMARY_JSON],
            "has_more": False,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=list_json))
            page = listings.list()
        item = page.data[0]
        assert not hasattr(item, "stock")
        assert not hasattr(item, "has_deliverables")
        assert not hasattr(item, "short_code")
        assert not hasattr(item, "has_cover")

    def test_list_with_status_filter(self, listings):
        list_json = {"object": "list", "data": [], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=list_json))
            listings.list(status="archived")
        assert "status=archived" in str(route.calls[0].request.url)


class TestUpdateListing:
    def test_update_returns_listing_detail_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.update("lst_abc123", name="Updated Name")
        assert isinstance(result, ListingDetailResponse)

    def test_update_with_deliverable_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            listings.update("lst_abc123", deliverable=Deliverable.url("https://example.com/new"))
        body = json.loads(route.calls[0].request.content)
        # deliverable uses "content" key
        assert body["deliverable"] == {"type": "url", "content": "https://example.com/new"}

    def test_update_with_image_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            listings.update("lst_abc123", image_url="https://cdn.example.com/new.jpg")
        body = json.loads(route.calls[0].request.content)
        assert body["image_url"] == "https://cdn.example.com/new.jpg"

    def test_update_with_agent_callback_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(
                return_value=httpx.Response(200, json=ASYNC_LISTING_DETAIL_JSON)
            )
            listings.update("lst_abc123", agent_callback_url="https://yourapp.com/webhooks/listbee")
        body = json.loads(route.calls[0].request.content)
        assert body["agent_callback_url"] == "https://yourapp.com/webhooks/listbee"

    def test_update_omits_none_fields(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            listings.update("lst_abc123", name="New Name")
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "New Name"}

    def test_update_with_signing_secret_rotate_returns_rotate_response(self, listings):
        rotate_response = {
            "object": "rotate_signing_secret",
            "listing": LISTING_DETAIL_JSON,
            "signing_secret": "new-long-signing-secret-value",
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=rotate_response))
            result = listings.update("lst_abc123", signing_secret="rotate")
        assert isinstance(result, RotateSigningSecretResponse)
        assert result.signing_secret == "new-long-signing-secret-value"
        assert isinstance(result.listing, ListingDetailResponse)

    def test_update_no_deprecated_params(self, listings):
        """Verify fulfillment_mode, cover_blur, utm_* are not accepted."""
        # These params were removed in the rebaseline; the method signature should not have them
        import inspect

        sig = inspect.signature(listings.update)
        removed_params = ["fulfillment_mode", "cover_blur", "utm_source", "utm_medium", "utm_campaign"]
        for param in removed_params:
            assert param not in sig.parameters, f"Deprecated param still present: {param}"


class TestPublishListing:
    def test_publish_returns_listing_detail_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/publish").mock(
                return_value=httpx.Response(200, json=LISTING_DETAIL_JSON)
            )
            result = listings.publish("lst_abc123")
        assert isinstance(result, ListingDetailResponse)

    def test_publish_sends_to_correct_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/lst_abc123/publish").mock(
                return_value=httpx.Response(200, json=LISTING_DETAIL_JSON)
            )
            listings.publish("lst_abc123")
        assert route.called


class TestUnpublishListing:
    def test_unpublish_returns_listing_detail_response(self, listings):
        draft_listing = {**LISTING_DETAIL_JSON, "status": "draft"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/unpublish").mock(return_value=httpx.Response(200, json=draft_listing))
            result = listings.unpublish("lst_abc123")
        assert isinstance(result, ListingDetailResponse)
        assert result.status == "draft"

    def test_unpublish_sends_to_correct_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/lst_abc123/unpublish").mock(
                return_value=httpx.Response(200, json={**LISTING_DETAIL_JSON, "status": "draft"})
            )
            listings.unpublish("lst_abc123")
        assert route.called


class TestArchiveListing:
    def test_archive_returns_listing_detail_response(self, listings):
        archived_listing = {**LISTING_DETAIL_JSON, "status": "archived"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/archive").mock(return_value=httpx.Response(200, json=archived_listing))
            result = listings.archive("lst_abc123")
        assert isinstance(result, ListingDetailResponse)
        assert result.status == "archived"
        assert result.is_archived is True

    def test_archive_sends_to_correct_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/lst_abc123/archive").mock(
                return_value=httpx.Response(200, json={**LISTING_DETAIL_JSON, "status": "archived"})
            )
            listings.archive("lst_abc123")
        assert route.called


class TestListingStatusHelpers:
    def test_is_draft_property(self, listings):
        draft = {**LISTING_DETAIL_JSON, "status": "draft"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=draft))
            result = listings.get("lst_abc123")
        assert result.is_draft is True
        assert result.is_published is False
        assert result.is_archived is False

    def test_is_archived_property(self, listings):
        archived = {**LISTING_DETAIL_JSON, "status": "archived"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=archived))
            result = listings.get("lst_abc123")
        assert result.is_archived is True
        assert result.is_published is False
        assert result.is_draft is False


class TestListingMetadata:
    def test_create_listing_with_metadata(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=CREATE_RESPONSE_JSON))
            listings.create(name="Test", price=100, metadata={"source": "n8n", "campaign": "launch-week"})
        body = json.loads(route.calls[0].request.content)
        assert body["metadata"] == {"source": "n8n", "campaign": "launch-week"}

    def test_listing_response_includes_metadata(self, listings):
        with_meta = {**LISTING_DETAIL_JSON, "metadata": {"source": "n8n"}}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=with_meta))
            result = listings.get("lst_abc123")
        assert result.metadata == {"source": "n8n"}


class TestDeleteListing:
    def test_delete_listing_returns_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/listings/lst_abc123").mock(return_value=httpx.Response(204))
            result = listings.delete("lst_abc123")
        assert result is None

    def test_delete_listing_sends_delete_request(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/listings/lst_abc123").mock(return_value=httpx.Response(204))
            listings.delete("lst_abc123")
        assert route.called


class TestListingReadinessBuyable:
    def test_buyable_true(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_DETAIL_JSON))
            result = listings.get("lst_abc123")
        assert result.readiness.buyable is True
        assert result.readiness.is_ready is True

    def test_buyable_false_with_actions(self, listings):
        not_buyable = {
            **LISTING_DETAIL_JSON,
            "readiness": {
                "buyable": False,
                "actions": [
                    {
                        "code": "stripe_connect_required",
                        "kind": "api",
                        "message": "Connect your Stripe account",
                        "resolve": {
                            "method": "POST",
                            "endpoint": "/v1/account/stripe-connect-session",
                            "url": None,
                            "params": None,
                        },
                    }
                ],
                "next": "stripe_connect_required",
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=not_buyable))
            result = listings.get("lst_abc123")
        assert result.readiness.buyable is False
        assert result.readiness.is_ready is False
        assert result.readiness.next == "stripe_connect_required"
        assert result.readiness.next_action is not None
        assert result.readiness.next_action.code == "stripe_connect_required"
