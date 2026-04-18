"""Tests for the Listings resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.deliverable import Deliverable
from listbee.resources.listings import Listings
from listbee.types.listing import ListingResponse, ListingSummary

# Base listing fixture matching the new API schema
LISTING_JSON = {
    "object": "listing",
    "id": "lst_abc123",
    "short_code": "r7kq2xy",
    "name": "SEO Playbook",
    "description": None,
    "tagline": None,
    "highlights": [],
    "cta": None,
    "price": 2900,
    "fulfillment_mode": "static",
    "deliverable": {
        "object": "deliverable",
        "id": "del_existing_001",
        "type": "url",
        "status": "ready",
        "url": "https://example.com/ebook",
        "content": None,
    },
    "agent_callback_url": None,
    "signing_secret_preview": "a1b2",
    "has_cover": True,
    "embed_url": None,
    "checkout_schema": None,
    "compare_at_price": None,
    "badges": [],
    "cover_blur": "auto",
    "rating": None,
    "rating_count": None,
    "reviews": [],
    "faqs": [],
    "metadata": None,
    "utm_source": None,
    "utm_medium": None,
    "utm_campaign": None,
    "status": "published",
    "url": "https://buy.listbee.so/seo-playbook",
    "readiness": {"sellable": True, "actions": [], "next": None},
    "created_at": "2026-03-30T12:00:00Z",
}

# Async-mode listing with agent_callback_url
ASYNC_LISTING_JSON = {
    **LISTING_JSON,
    "id": "lst_ext456",
    "short_code": "m3pr5tw",
    "name": "Custom Service",
    "fulfillment_mode": "async",
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
    "short_code": "r7kq2xy",
    "name": "SEO Playbook",
    "tagline": None,
    "price": 2900,
    "compare_at_price": None,
    "cta": None,
    "badges": [],
    "highlights": [],
    "status": "published",
    "fulfillment_mode": "static",
    "has_cover": True,
    "url": "https://buy.listbee.so/seo-playbook",
    "created_at": "2026-03-30T12:00:00Z",
}


@pytest.fixture
def sync_client():
    return SyncClient(api_key="lb_test")


@pytest.fixture
def listings(sync_client):
    return Listings(sync_client)


class TestCreateListing:
    def test_create_listing_returns_listing_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.create(name="SEO Playbook", price=2999)
        assert isinstance(result, ListingResponse)
        assert result.id == "lst_abc123"
        assert result.short_code == "r7kq2xy"
        assert result.name == "SEO Playbook"
        assert result.price == 2900
        assert result.status == "published"
        assert result.fulfillment_mode == "static"

    def test_create_listing_with_deliverable_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="Test",
                price=100,
                deliverable=Deliverable.url("https://example.com/secret"),
            )
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == {"type": "url", "value": "https://example.com/secret"}

    def test_create_listing_with_text_deliverable(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="Test",
                price=100,
                deliverable=Deliverable.text("License: ABCD-1234"),
            )
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == {"type": "text", "value": "License: ABCD-1234"}

    def test_create_listing_with_fulfillment_mode_async(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=ASYNC_LISTING_JSON))
            listings.create(
                name="Custom Service",
                price=5000,
                fulfillment_mode="async",
                agent_callback_url="https://yourapp.com/webhooks/listbee",
            )
        body = json.loads(route.calls[0].request.content)
        assert body["fulfillment_mode"] == "async"
        assert body["agent_callback_url"] == "https://yourapp.com/webhooks/listbee"

    def test_create_listing_with_readiness_actions(self, listings):
        json_with_actions = {
            **LISTING_JSON,
            "readiness": {
                "sellable": False,
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
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=json_with_actions))
            result = listings.create(name="SEO Playbook", price=2999)
        assert result.readiness.sellable is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "stripe_connect_required"
        assert result.readiness.actions[0].kind == "api"
        assert result.readiness.actions[0].resolve.endpoint == "/v1/account/stripe-connect-session"
        assert result.readiness.next == "stripe_connect_required"

    def test_create_listing_optional_fields_omitted_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="SEO Playbook", price=2999)
        body = json.loads(route.calls[0].request.content)
        assert "description" not in body
        assert "tagline" not in body
        assert "cover_blur" not in body  # default "auto" is not sent
        assert "deliverable" not in body  # not sent when None
        assert "fulfillment_url" not in body  # removed field

    def test_create_listing_cover_blur_sent_when_not_auto(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, cover_blur="true")
        body = json.loads(route.calls[0].request.content)
        assert body["cover_blur"] == "true"

    def test_create_listing_with_checkout_schema(self, listings):
        schema = [{"key": "shirt_size", "label": "Shirt Size", "type": "select", "options": ["S", "M", "L"]}]
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=ASYNC_LISTING_JSON))
            listings.create(name="T-Shirt", price=2500, checkout_schema=schema)
        body = json.loads(route.calls[0].request.content)
        assert body["checkout_schema"] == schema

    def test_create_listing_with_checkout_field_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=ASYNC_LISTING_JSON))
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
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, signing_secret="my_secret")
        body = json.loads(route.calls[0].request.content)
        assert body["signing_secret"] == "my_secret"


class TestGetListing:
    def test_get_listing_by_id(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert isinstance(result, ListingResponse)
        assert result.short_code == "r7kq2xy"
        assert result.id == "lst_abc123"

    def test_get_listing_sends_correct_path(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.get("lst_abc123")
        assert route.called

    def test_listing_response_has_single_deliverable(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert result.deliverable is not None
        assert result.deliverable.type == "url"
        assert result.deliverable.status == "ready"

    def test_listing_response_has_signing_secret_preview(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert result.signing_secret_preview == "a1b2"

    def test_listing_response_async_mode(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_ext456").mock(return_value=httpx.Response(200, json=ASYNC_LISTING_JSON))
            result = listings.get("lst_ext456")
        assert result.fulfillment_mode == "async"
        assert result.agent_callback_url == "https://yourapp.com/webhooks/listbee"
        assert result.deliverable is None
        assert result.checkout_schema is not None
        assert len(result.checkout_schema) == 1
        assert result.checkout_schema[0].key == "shirt_size"
        assert result.checkout_schema[0].type == "select"
        assert result.checkout_schema[0].options == ["S", "M", "L", "XL"]
        assert result.checkout_schema[0].sort_order == 0

    def test_listing_response_has_no_old_fields(self, listings):
        """Verify removed fields are not present."""
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert not hasattr(result, "fulfillment_url")
        assert not hasattr(result, "has_deliverables")
        assert not hasattr(result, "stock")
        assert not hasattr(result, "deliverables")


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
        assert page.data[0].fulfillment_mode == "static"

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

    def test_list_with_status_filter(self, listings):
        list_json = {"object": "list", "data": [], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=list_json))
            listings.list(status="archived")
        assert "status=archived" in str(route.calls[0].request.url)


class TestUpdateListing:
    def test_update_returns_listing_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.update("lst_abc123", name="Updated Name")
        assert isinstance(result, ListingResponse)

    def test_update_with_deliverable_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", deliverable=Deliverable.url("https://example.com/new"))
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == {"type": "url", "value": "https://example.com/new"}

    def test_update_with_agent_callback_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=ASYNC_LISTING_JSON))
            listings.update("lst_abc123", agent_callback_url="https://yourapp.com/webhooks/listbee")
        body = json.loads(route.calls[0].request.content)
        assert body["agent_callback_url"] == "https://yourapp.com/webhooks/listbee"

    def test_update_omits_none_fields(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", name="New Name")
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "New Name"}

    def test_update_with_fulfillment_mode(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", fulfillment_mode="async")
        body = json.loads(route.calls[0].request.content)
        assert body["fulfillment_mode"] == "async"


class TestPublishListing:
    def test_publish_returns_listing_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/publish").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.publish("lst_abc123")
        assert isinstance(result, ListingResponse)

    def test_publish_sends_to_correct_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/lst_abc123/publish").mock(
                return_value=httpx.Response(200, json=LISTING_JSON)
            )
            listings.publish("lst_abc123")
        assert route.called


class TestUnpublishListing:
    def test_unpublish_returns_listing_response(self, listings):
        draft_listing = {**LISTING_JSON, "status": "draft"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/unpublish").mock(return_value=httpx.Response(200, json=draft_listing))
            result = listings.unpublish("lst_abc123")
        assert isinstance(result, ListingResponse)
        assert result.status == "draft"

    def test_unpublish_sends_to_correct_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/lst_abc123/unpublish").mock(
                return_value=httpx.Response(200, json={**LISTING_JSON, "status": "draft"})
            )
            listings.unpublish("lst_abc123")
        assert route.called


class TestArchiveListing:
    def test_archive_returns_listing_response(self, listings):
        archived_listing = {**LISTING_JSON, "status": "archived"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/archive").mock(return_value=httpx.Response(200, json=archived_listing))
            result = listings.archive("lst_abc123")
        assert isinstance(result, ListingResponse)
        assert result.status == "archived"
        assert result.is_archived is True

    def test_archive_sends_to_correct_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/lst_abc123/archive").mock(
                return_value=httpx.Response(200, json={**LISTING_JSON, "status": "archived"})
            )
            listings.archive("lst_abc123")
        assert route.called


class TestListingStatusHelpers:
    def test_is_draft_property(self, listings):
        draft = {**LISTING_JSON, "status": "draft"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=draft))
            result = listings.get("lst_abc123")
        assert result.is_draft is True
        assert result.is_published is False
        assert result.is_archived is False

    def test_is_archived_property(self, listings):
        archived = {**LISTING_JSON, "status": "archived"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=archived))
            result = listings.get("lst_abc123")
        assert result.is_archived is True
        assert result.is_published is False
        assert result.is_draft is False


class TestListingMetadata:
    def test_create_listing_with_metadata(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, metadata={"source": "n8n", "campaign": "launch-week"})
        body = json.loads(route.calls[0].request.content)
        assert body["metadata"] == {"source": "n8n", "campaign": "launch-week"}

    def test_listing_response_includes_metadata(self, listings):
        with_meta = {**LISTING_JSON, "metadata": {"source": "n8n"}}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=with_meta))
            result = listings.get("lst_abc123")
        assert result.metadata == {"source": "n8n"}


class TestUtmFields:
    def test_create_listing_sends_utm_params(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="Test",
                price=2900,
                utm_source="twitter",
                utm_medium="social",
                utm_campaign="launch-week",
            )
        body = json.loads(route.calls[0].request.content)
        assert body["utm_source"] == "twitter"
        assert body["utm_medium"] == "social"
        assert body["utm_campaign"] == "launch-week"

    def test_create_listing_omits_utm_params_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=2900)
        body = json.loads(route.calls[0].request.content)
        assert "utm_source" not in body
        assert "utm_medium" not in body
        assert "utm_campaign" not in body

    def test_update_listing_sends_utm_params(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", utm_source="newsletter", utm_campaign="spring-sale")
        body = json.loads(route.calls[0].request.content)
        assert body["utm_source"] == "newsletter"
        assert body["utm_campaign"] == "spring-sale"
        assert "utm_medium" not in body

    def test_listing_response_includes_utm_fields(self, listings):
        listing_with_utm = {**LISTING_JSON, "utm_source": "twitter", "utm_medium": "social", "utm_campaign": "launch"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=listing_with_utm))
            result = listings.get("lst_abc123")
        assert result.utm_source == "twitter"
        assert result.utm_medium == "social"
        assert result.utm_campaign == "launch"

    def test_listing_response_utm_fields_default_to_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert result.utm_source is None
        assert result.utm_medium is None
        assert result.utm_campaign is None


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
