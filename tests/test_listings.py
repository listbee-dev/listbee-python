"""Tests for the Listings resource."""

from __future__ import annotations

import io
import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee._exceptions import ListBeeError
from listbee.deliverable import Deliverable
from listbee.resources.listings import Listings
from listbee.types.listing import ListingResponse, ListingSummary

LISTING_JSON = {
    "object": "listing",
    "id": "lst_abc123",
    "slug": "seo-playbook",
    "name": "SEO Playbook",
    "description": None,
    "tagline": None,
    "highlights": [],
    "cta": None,
    "price": 2900,
    "fulfillment_url": None,
    "has_deliverables": True,
    "deliverables": [
        {
            "object": "deliverable",
            "id": "del_existing_001",
            "type": "file",
            "status": "ready",
            "content": None,
            "filename": "ebook.pdf",
            "mime_type": "application/pdf",
            "size": 2458631,
            "url": None,
        }
    ],
    "has_cover": True,
    "stock": None,
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

WEBHOOK_LISTING_JSON = {
    **LISTING_JSON,
    "id": "lst_ext456",
    "slug": "custom-service",
    "name": "Custom Service",
    "fulfillment_url": "https://yourapp.com/webhooks/fulfill",
    "has_deliverables": False,
    "deliverables": [],
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

# Keep EXTERNAL_LISTING_JSON as an alias for backwards compatibility in tests
EXTERNAL_LISTING_JSON = WEBHOOK_LISTING_JSON

LISTING_SUMMARY_JSON = {
    "object": "listing",
    "id": "lst_abc123",
    "slug": "seo-playbook",
    "name": "SEO Playbook",
    "tagline": None,
    "price": 2900,
    "compare_at_price": None,
    "cta": None,
    "badges": [],
    "highlights": [],
    "status": "published",
    "stock": None,
    "has_deliverables": True,
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
            result = listings.create(name="SEO Playbook", price=2999, deliverable="https://example.com/file.pdf")
        assert isinstance(result, ListingResponse)
        assert result.id == "lst_abc123"
        assert result.slug == "seo-playbook"
        assert result.name == "SEO Playbook"
        assert result.price == 2900
        assert result.status == "published"

    def test_create_listing_with_readiness_actions(self, listings):
        json_with_actions = {
            **LISTING_JSON,
            "readiness": {
                "sellable": False,
                "actions": [
                    {
                        "code": "connect_stripe",
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
                "next": "connect_stripe",
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=json_with_actions))
            result = listings.create(name="SEO Playbook", price=2999, deliverable="text content")
        assert result.readiness.sellable is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "connect_stripe"
        assert result.readiness.actions[0].kind == "api"
        assert result.readiness.actions[0].resolve.endpoint == "/v1/account/stripe-connect-session"
        assert result.readiness.next == "connect_stripe"

    def test_create_listing_optional_fields_omitted_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="SEO Playbook", price=2999, deliverable="text")
        body = json.loads(route.calls[0].request.content)
        assert "description" not in body
        assert "tagline" not in body
        assert "cover_blur" not in body  # default "auto" is not sent
        assert "fulfillment_url" not in body  # not sent when None

    def test_create_listing_cover_blur_sent_when_not_auto(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, deliverable="text", cover_blur="true")
        body = json.loads(route.calls[0].request.content)
        assert body["cover_blur"] == "true"

    def test_create_listing_sends_deliverable_in_body(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, deliverable="https://example.com/file.pdf")
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == "https://example.com/file.pdf"
        assert "content" not in body

    def test_create_listing_with_fulfillment_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=WEBHOOK_LISTING_JSON))
            listings.create(
                name="Custom Service",
                price=5000,
                fulfillment_url="https://yourapp.com/webhooks/fulfill",
            )
        body = json.loads(route.calls[0].request.content)
        assert body["fulfillment_url"] == "https://yourapp.com/webhooks/fulfill"

    def test_create_listing_without_fulfillment_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, deliverable="https://example.com/file.pdf")
        body = json.loads(route.calls[0].request.content)
        assert "fulfillment_url" not in body

    def test_create_listing_with_checkout_schema(self, listings):
        schema = [{"name": "shirt_size", "label": "Shirt Size", "type": "select", "options": ["S", "M", "L"]}]
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=WEBHOOK_LISTING_JSON))
            listings.create(name="T-Shirt", price=2500, checkout_schema=schema)
        body = json.loads(route.calls[0].request.content)
        assert body["checkout_schema"] == schema

    def test_create_listing_with_checkout_field_builder(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=WEBHOOK_LISTING_JSON))
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


class TestGetListing:
    def test_get_listing_by_id(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert isinstance(result, ListingResponse)
        assert result.slug == "seo-playbook"
        assert result.id == "lst_abc123"

    def test_get_listing_sends_correct_path(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.get("lst_abc123")
        assert route.called


class TestListListings:
    def test_list_listings_returns_summary_items_via_auto_iteration(self, listings):
        page_json = {
            "data": [LISTING_SUMMARY_JSON],
            "has_more": False,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            results = list(listings.list())
        assert len(results) == 1
        assert isinstance(results[0], ListingSummary)
        assert results[0].id == "lst_abc123"

    def test_list_listings_has_more_and_cursor(self, listings):
        page_json = {
            "data": [LISTING_SUMMARY_JSON],
            "has_more": True,
            "cursor": "next_cursor",
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            page = listings.list()
        assert page.has_more is True
        assert page.cursor == "next_cursor"

    def test_list_listings_empty(self, listings):
        page_json = {"data": [], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            results = list(listings.list())
        assert results == []

    def test_list_listings_passes_limit_param(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(
                return_value=httpx.Response(200, json={"data": [], "has_more": False, "cursor": None})
            )
            list(listings.list(limit=5))
        assert "limit=5" in str(route.calls[0].request.url)

    def test_list_listings_with_status_filter(self, listings):
        page_json = {"data": [LISTING_SUMMARY_JSON], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            list(listings.list(status="published"))
        assert "status=published" in str(route.calls[0].request.url)

    def test_list_listings_without_status_omits_param(self, listings):
        page_json = {"data": [], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            list(listings.list())
        assert "status" not in str(route.calls[0].request.url)

    def test_list_listings_summary_fields(self, listings):
        page_json = {"data": [LISTING_SUMMARY_JSON], "has_more": False, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            results = list(listings.list())
        item = results[0]
        assert item.slug == "seo-playbook"
        assert item.price == 2900
        assert item.status == "published"
        assert item.has_deliverables is True
        assert item.has_cover is True
        assert item.url == "https://buy.listbee.so/seo-playbook"


class TestUpdateListing:
    def test_update_sends_only_provided_fields(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", name="Updated Name", price=3900)
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Updated Name", "price": 3900}
        assert "description" not in body

    def test_update_returns_listing_response(self, listings):
        updated = {**LISTING_JSON, "name": "Updated Name", "price": 3900}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=updated))
            result = listings.update("lst_abc123", name="Updated Name", price=3900)
        assert isinstance(result, ListingResponse)
        assert result.name == "Updated Name"
        assert result.price == 3900

    def test_update_with_fulfillment_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", fulfillment_url="https://yourapp.com/fulfill")
        body = json.loads(route.calls[0].request.content)
        assert body["fulfillment_url"] == "https://yourapp.com/fulfill"

    def test_update_with_checkout_schema(self, listings):
        schema = [{"name": "color", "label": "Color", "type": "select", "options": ["Red", "Blue"]}]
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("lst_abc123", checkout_schema=schema)
        body = json.loads(route.calls[0].request.content)
        assert body["checkout_schema"] == schema


class TestDeleteListing:
    def test_delete_listing_sends_delete_request(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/listings/lst_abc123").mock(return_value=httpx.Response(204))
            result = listings.delete("lst_abc123")
        assert route.called
        assert result is None


class TestFulfillmentFields:
    def test_listing_response_has_deliverables_true(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("lst_abc123")
        assert result.has_deliverables is True
        assert len(result.deliverables) == 1
        assert result.deliverables[0].type == "file"
        assert result.deliverables[0].status == "ready"
        assert result.checkout_schema is None

    def test_listing_response_with_fulfillment_url(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_ext456").mock(return_value=httpx.Response(200, json=WEBHOOK_LISTING_JSON))
            result = listings.get("lst_ext456")
        assert result.fulfillment_url == "https://yourapp.com/webhooks/fulfill"
        assert result.has_deliverables is False
        assert result.deliverables == []
        assert result.checkout_schema is not None
        assert len(result.checkout_schema) == 1
        assert result.checkout_schema[0].key == "shirt_size"
        assert result.checkout_schema[0].type == "select"
        assert result.checkout_schema[0].options == ["S", "M", "L", "XL"]
        assert result.checkout_schema[0].sort_order == 0

    def test_listing_response_no_fulfillment_url(self, listings):
        no_url_json = {**LISTING_JSON, "fulfillment_url": None, "has_deliverables": False, "deliverables": []}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=no_url_json))
            result = listings.get("lst_abc123")
        assert result.fulfillment_url is None
        assert result.has_deliverables is False

    def test_listing_response_configure_webhook_action(self, listings):
        json_with_webhook_action = {
            **LISTING_JSON,
            "readiness": {
                "sellable": False,
                "actions": [
                    {
                        "code": "configure_webhook",
                        "kind": "api",
                        "message": "Configure a webhook endpoint to receive order.paid events",
                        "resolve": {
                            "method": "POST",
                            "endpoint": "/v1/webhooks",
                            "url": None,
                            "params": None,
                        },
                    }
                ],
                "next": "configure_webhook",
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/lst_abc123").mock(return_value=httpx.Response(200, json=json_with_webhook_action))
            result = listings.get("lst_abc123")
        assert result.readiness.sellable is False
        assert result.readiness.actions[0].code == "configure_webhook"
        assert result.readiness.next == "configure_webhook"


class TestUtmFields:
    def test_create_listing_sends_utm_params(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="Test",
                price=2900,
                deliverable="text",
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
            listings.create(name="Test", price=2900, deliverable="text")
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


class TestSetDeliverables:
    def test_set_deliverables_returns_listing_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/lst_abc123/deliverables").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.set_deliverables(
                "lst_abc123",
                deliverables=[{"type": "url", "value": "https://example.com/ebook.pdf"}],
            )
        assert isinstance(result, ListingResponse)

    def test_set_deliverables_sends_correct_body(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/lst_abc123/deliverables").mock(
                return_value=httpx.Response(200, json=LISTING_JSON)
            )
            listings.set_deliverables(
                "lst_abc123",
                deliverables=[
                    {"type": "file", "token": "file_abc"},
                    {"type": "text", "value": "License key: ABC-123"},
                ],
            )
        body = json.loads(route.calls[0].request.content)
        assert len(body["deliverables"]) == 2
        assert body["deliverables"][0]["type"] == "file"
        assert body["deliverables"][0]["token"] == "file_abc"


class TestRemoveDeliverables:
    def test_remove_deliverables_returns_listing_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.delete("/v1/listings/lst_abc123/deliverables").mock(
                return_value=httpx.Response(200, json=LISTING_JSON)
            )
            result = listings.remove_deliverables("lst_abc123")
        assert isinstance(result, ListingResponse)


class TestPublishListing:
    def test_publish_returns_listing_response(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/lst_abc123/publish").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.publish("lst_abc123")
        assert isinstance(result, ListingResponse)


DELIVERABLE_JSON = {
    "object": "deliverable",
    "id": "del_abc123",
    "type": "url",
    "status": "ready",
    "filename": None,
    "size": None,
    "mime_type": None,
    "url": "https://example.com/secret",
    "content": None,
}

FILE_JSON = {
    "object": "file",
    "id": "file_tok_abc",
    "filename": "guide.pdf",
    "size": 1024,
    "mime_type": "application/pdf",
    "purpose": "deliverable",
    "expires_at": "2026-04-07T12:00:00Z",
    "created_at": "2026-04-06T12:00:00Z",
}


class TestAddDeliverable:
    @respx.mock
    def test_add_url(self, sync_client):
        respx.post("https://api.listbee.so/v1/listings/lst_abc123/deliverables").mock(
            return_value=httpx.Response(201, json=DELIVERABLE_JSON)
        )
        result = Listings(sync_client).add_deliverable("lst_abc123", Deliverable.url("https://example.com/secret"))
        assert result.id == "del_abc123"
        assert result.type == "url"

    @respx.mock
    def test_add_text(self, sync_client):
        route = respx.post("https://api.listbee.so/v1/listings/lst_abc123/deliverables").mock(
            return_value=httpx.Response(201, json=DELIVERABLE_JSON | {"type": "text"})
        )
        Listings(sync_client).add_deliverable("lst_abc123", Deliverable.text("License: ABCD"))
        sent = json.loads(route.calls[0].request.content)
        assert sent == {"type": "text", "value": "License: ABCD"}

    @respx.mock
    def test_add_file_uploads_first(self, sync_client):
        respx.post("https://api.listbee.so/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
        route = respx.post("https://api.listbee.so/v1/listings/lst_abc123/deliverables").mock(
            return_value=httpx.Response(201, json=DELIVERABLE_JSON | {"type": "file"})
        )
        Listings(sync_client).add_deliverable("lst_abc123", Deliverable.file(b"pdf-bytes", filename="guide.pdf"))
        sent = json.loads(route.calls[0].request.content)
        assert sent == {"type": "file", "token": "file_tok_abc"}

    @respx.mock
    def test_add_from_token_no_upload(self, sync_client):
        route = respx.post("https://api.listbee.so/v1/listings/lst_abc123/deliverables").mock(
            return_value=httpx.Response(201, json=DELIVERABLE_JSON | {"type": "file"})
        )
        Listings(sync_client).add_deliverable("lst_abc123", Deliverable.from_token("file_tok_existing"))
        sent = json.loads(route.calls[0].request.content)
        assert sent == {"type": "file", "token": "file_tok_existing"}


class TestRemoveOneDeliverable:
    @respx.mock
    def test_remove_deliverable(self, sync_client):
        respx.delete("https://api.listbee.so/v1/listings/lst_abc123/deliverables/del_xyz").mock(
            return_value=httpx.Response(204)
        )
        Listings(sync_client).remove_deliverable("lst_abc123", "del_xyz")


class TestSetDeliverablesWithClass:
    @respx.mock
    def test_set_with_deliverable_objects(self, sync_client):
        respx.post("https://api.listbee.so/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
        respx.put("https://api.listbee.so/v1/listings/lst_abc123/deliverables").mock(
            return_value=httpx.Response(200, json=LISTING_JSON)
        )
        Listings(sync_client).set_deliverables(
            "lst_abc123",
            deliverables=[
                Deliverable.file(b"content", filename="a.pdf"),
                Deliverable.url("https://example.com"),
            ],
        )


class TestCreateComplete:
    @respx.mock
    def test_create_with_deliverables(self, sync_client):
        respx.post("https://api.listbee.so/v1/listings").mock(
            return_value=httpx.Response(201, json=LISTING_JSON | {"id": "lst_new", "deliverables": []})
        )
        respx.post("https://api.listbee.so/v1/files").mock(return_value=httpx.Response(201, json=FILE_JSON))
        respx.post("https://api.listbee.so/v1/listings/lst_new/deliverables").mock(
            return_value=httpx.Response(201, json=DELIVERABLE_JSON)
        )
        respx.get("https://api.listbee.so/v1/listings/lst_new").mock(
            return_value=httpx.Response(200, json=LISTING_JSON | {"id": "lst_new"})
        )
        result = Listings(sync_client).create_complete(
            name="Test",
            price=999,
            deliverables=[
                Deliverable.file(b"pdf-bytes", filename="guide.pdf"),
                Deliverable.url("https://example.com"),
            ],
        )
        assert result.id == "lst_new"

    @respx.mock
    def test_create_without_deliverables(self, sync_client):
        respx.post("https://api.listbee.so/v1/listings").mock(
            return_value=httpx.Response(
                201,
                json=LISTING_JSON
                | {"id": "lst_new", "deliverables": [], "has_deliverables": False, "fulfillment_url": None},
            )
        )
        result = Listings(sync_client).create_complete(name="Test", price=999)
        assert result.id == "lst_new"

    @respx.mock
    def test_partial_creation_error(self, sync_client):
        from listbee._exceptions import PartialCreationError

        respx.post("https://api.listbee.so/v1/listings").mock(
            return_value=httpx.Response(201, json=LISTING_JSON | {"id": "lst_new", "deliverables": []})
        )
        respx.post("https://api.listbee.so/v1/files").mock(
            return_value=httpx.Response(
                500, json={"type": "internal", "title": "Error", "status": 500, "detail": "fail", "code": "internal"}
            )
        )
        with pytest.raises(PartialCreationError) as exc_info:
            Listings(sync_client).create_complete(
                name="Test",
                price=999,
                deliverables=[Deliverable.file(b"x", filename="f.pdf")],
            )
        assert exc_info.value.listing_id == "lst_new"


COVER_FILE_JSON = {
    "object": "file",
    "id": "file_covertoken456",
    "filename": "cover.jpeg",
    "size": 2048,
    "mime_type": "image/jpeg",
    "purpose": "cover",
    "expires_at": "2026-04-11T15:00:00Z",
    "created_at": "2026-04-10T15:00:00Z",
}


class TestSetCover:
    @respx.mock
    def test_set_cover_with_file_token_passes_directly(self, sync_client):
        """file_ token goes straight to update without uploading."""
        respx.put("https://api.listbee.so/v1/listings/lst_abc123").mock(
            return_value=httpx.Response(200, json=LISTING_JSON)
        )
        result = Listings(sync_client).set_cover("lst_abc123", "file_covertoken456")
        assert isinstance(result, ListingResponse)
        # No upload call should have been made
        assert all(call.request.url.path != "/v1/files" for route in respx.mock.routes for call in route.calls)

    @respx.mock
    def test_set_cover_with_bytes_uploads_then_updates(self, sync_client):
        """bytes input triggers upload then update."""
        image_bytes = b"\xff\xd8\xff\xe0fake-jpeg"
        upload_route = respx.post("https://api.listbee.so/v1/files").mock(
            return_value=httpx.Response(201, json=COVER_FILE_JSON)
        )
        update_route = respx.put("https://api.listbee.so/v1/listings/lst_abc123").mock(
            return_value=httpx.Response(200, json=LISTING_JSON)
        )
        result = Listings(sync_client).set_cover("lst_abc123", image_bytes)
        assert upload_route.call_count == 1
        body = json.loads(update_route.calls[0].request.content)
        assert body["cover_url"] == "file_covertoken456"
        assert isinstance(result, ListingResponse)

    @respx.mock
    def test_set_cover_with_binary_io_uploads_then_updates(self, sync_client):
        """BinaryIO input triggers upload then update."""
        image_bytes = b"\xff\xd8\xff\xe0fake-jpeg"
        buf = io.BytesIO(image_bytes)
        buf.name = "my_cover.jpg"
        upload_route = respx.post("https://api.listbee.so/v1/files").mock(
            return_value=httpx.Response(201, json=COVER_FILE_JSON)
        )
        update_route = respx.put("https://api.listbee.so/v1/listings/lst_abc123").mock(
            return_value=httpx.Response(200, json=LISTING_JSON)
        )
        result = Listings(sync_client).set_cover("lst_abc123", buf)
        assert upload_route.call_count == 1
        body = json.loads(update_route.calls[0].request.content)
        assert body["cover_url"] == "file_covertoken456"
        assert isinstance(result, ListingResponse)

    @respx.mock
    def test_set_cover_with_url_uploads_then_updates(self, sync_client):
        """URL input fetches image, uploads with purpose=cover, then updates."""
        image_bytes = b"\xff\xd8\xff\xe0fake-jpeg"
        upload_route = respx.post("https://api.listbee.so/v1/files").mock(
            return_value=httpx.Response(201, json=COVER_FILE_JSON)
        )
        update_route = respx.put("https://api.listbee.so/v1/listings/lst_abc123").mock(
            return_value=httpx.Response(200, json=LISTING_JSON)
        )
        with respx.mock(assert_all_called=False) as url_mock:
            url_mock.get("https://example.com/cover.jpg").mock(
                return_value=httpx.Response(
                    200,
                    content=image_bytes,
                    headers={"content-type": "image/jpeg"},
                )
            )
            result = Listings(sync_client).set_cover("lst_abc123", "https://example.com/cover.jpg")

        assert upload_route.call_count == 1
        # Verify purpose=cover was sent in multipart
        upload_body = upload_route.calls[0].request.content.decode(errors="replace")
        assert "cover" in upload_body
        body = json.loads(update_route.calls[0].request.content)
        assert body["cover_url"] == "file_covertoken456"
        assert isinstance(result, ListingResponse)

    def test_set_cover_url_non_image_raises(self, sync_client):
        """Non-image content-type from URL raises ListBeeError."""
        with respx.mock() as url_mock:
            url_mock.get("https://example.com/notimage.html").mock(
                return_value=httpx.Response(
                    200,
                    content=b"<html>",
                    headers={"content-type": "text/html"},
                )
            )
            with pytest.raises(ListBeeError, match="did not return an image"):
                Listings(sync_client).set_cover("lst_abc123", "https://example.com/notimage.html")

    def test_set_cover_url_http_error_raises(self, sync_client):
        """Non-200 URL response raises ListBeeError."""
        with respx.mock() as url_mock:
            url_mock.get("https://example.com/missing.jpg").mock(return_value=httpx.Response(404, content=b"not found"))
            with pytest.raises(ListBeeError, match="HTTP 404"):
                Listings(sync_client).set_cover("lst_abc123", "https://example.com/missing.jpg")
