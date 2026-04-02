"""Tests for the Listings resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from listbee._base_client import SyncClient
from listbee.resources.listings import Listings
from listbee.types.listing import ListingResponse

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
    "fulfillment": "managed",
    "deliverable_type": "file",
    "has_deliverable": True,
    "has_cover": True,
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
    "status": "active",
    "url": "https://buy.listbee.so/seo-playbook",
    "readiness": {"sellable": True, "actions": [], "next": None},
    "created_at": "2026-03-30T12:00:00Z",
}

EXTERNAL_LISTING_JSON = {
    **LISTING_JSON,
    "id": "lst_ext456",
    "slug": "custom-service",
    "name": "Custom Service",
    "fulfillment": "external",
    "deliverable_type": None,
    "has_deliverable": False,
    "checkout_schema": [
        {
            "name": "shirt_size",
            "label": "Shirt Size",
            "type": "select",
            "required": True,
            "options": ["S", "M", "L", "XL"],
        }
    ],
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
        assert result.status == "active"

    def test_create_listing_with_readiness_actions(self, listings):
        json_with_actions = {
            **LISTING_JSON,
            "readiness": {
                "sellable": False,
                "actions": [
                    {
                        "code": "set_stripe_key",
                        "kind": "api",
                        "message": "Set your Stripe secret key via the API",
                        "resolve": {
                            "method": "PUT",
                            "endpoint": "/v1/account/stripe",
                            "url": None,
                            "params": {"stripe_secret_key": "sk_..."},
                        },
                    }
                ],
                "next": "set_stripe_key",
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=json_with_actions))
            result = listings.create(name="SEO Playbook", price=2999, deliverable="text content")
        assert result.readiness.sellable is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "set_stripe_key"
        assert result.readiness.actions[0].kind == "api"
        assert result.readiness.actions[0].resolve.endpoint == "/v1/account/stripe"
        assert result.readiness.next == "set_stripe_key"

    def test_create_listing_optional_fields_omitted_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="SEO Playbook", price=2999, deliverable="text")
        body = json.loads(route.calls[0].request.content)
        assert "description" not in body
        assert "tagline" not in body
        assert "cover_blur" not in body  # default "auto" is not sent
        assert "fulfillment" not in body  # not sent when None

    def test_create_listing_cover_blur_sent_when_not_auto(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, deliverable="text", cover_blur="true")
        body = json.loads(route.calls[0].request.content)
        assert body["cover_blur"] == "true"

    def test_create_listing_with_store_id(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="SEO Playbook",
                price=2999,
                deliverable="https://example.com/file.pdf",
                store_id="str_7kQ2xY9mN3pR5tW1vB8a",
            )
        body = json.loads(route.calls[0].request.content)
        assert body["store_id"] == "str_7kQ2xY9mN3pR5tW1vB8a"

    def test_create_listing_sends_deliverable_in_body(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, deliverable="https://example.com/file.pdf")
        body = json.loads(route.calls[0].request.content)
        assert body["deliverable"] == "https://example.com/file.pdf"
        assert "content" not in body

    def test_create_listing_without_deliverable(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=EXTERNAL_LISTING_JSON))
            listings.create(name="Custom Service", price=5000, fulfillment="external")
        body = json.loads(route.calls[0].request.content)
        assert "deliverable" not in body
        assert body["fulfillment"] == "external"

    def test_create_listing_with_fulfillment_mode(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(
                name="Test", price=100, deliverable="https://example.com/file.pdf", fulfillment="managed"
            )
        body = json.loads(route.calls[0].request.content)
        assert body["fulfillment"] == "managed"

    def test_create_listing_with_checkout_schema(self, listings):
        schema = [{"name": "shirt_size", "label": "Shirt Size", "type": "select", "options": ["S", "M", "L"]}]
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=EXTERNAL_LISTING_JSON))
            listings.create(name="T-Shirt", price=2500, fulfillment="external", checkout_schema=schema)
        body = json.loads(route.calls[0].request.content)
        assert body["checkout_schema"] == schema


class TestGetListing:
    def test_get_listing_by_slug(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("seo-playbook")
        assert isinstance(result, ListingResponse)
        assert result.slug == "seo-playbook"
        assert result.id == "lst_abc123"

    def test_get_listing_sends_correct_path(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings/my-listing").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.get("my-listing")
        assert route.called


class TestListListings:
    def test_list_listings_returns_items_via_auto_iteration(self, listings):
        page_json = {
            "data": [LISTING_JSON],
            "has_more": False,
            "total_count": 1,
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            results = list(listings.list())
        assert len(results) == 1
        assert isinstance(results[0], ListingResponse)
        assert results[0].id == "lst_abc123"

    def test_list_listings_total_count(self, listings):
        page_json = {
            "data": [LISTING_JSON],
            "has_more": True,
            "total_count": 42,
            "cursor": "next_cursor",
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            page = listings.list()
        assert page.total_count == 42

    def test_list_listings_empty(self, listings):
        page_json = {"data": [], "has_more": False, "total_count": 0, "cursor": None}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            results = list(listings.list())
        assert results == []

    def test_list_listings_passes_limit_param(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/listings").mock(
                return_value=httpx.Response(200, json={"data": [], "has_more": False, "total_count": 0, "cursor": None})
            )
            list(listings.list(limit=5))
        assert "limit=5" in str(route.calls[0].request.url)


class TestUpdateListing:
    def test_update_sends_only_provided_fields(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("seo-playbook", name="Updated Name", price=3900)
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Updated Name", "price": 3900}
        assert "description" not in body

    def test_update_returns_listing_response(self, listings):
        updated = {**LISTING_JSON, "name": "Updated Name", "price": 3900}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=updated))
            result = listings.update("seo-playbook", name="Updated Name", price=3900)
        assert isinstance(result, ListingResponse)
        assert result.name == "Updated Name"
        assert result.price == 3900

    def test_update_with_fulfillment_mode(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("seo-playbook", fulfillment="external")
        body = json.loads(route.calls[0].request.content)
        assert body["fulfillment"] == "external"

    def test_update_with_checkout_schema(self, listings):
        schema = [{"name": "color", "label": "Color", "type": "select", "options": ["Red", "Blue"]}]
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.put("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("seo-playbook", checkout_schema=schema)
        body = json.loads(route.calls[0].request.content)
        assert body["checkout_schema"] == schema


class TestPauseListing:
    def test_pause_listing_returns_paused_response(self, listings):
        paused_json = {**LISTING_JSON, "status": "paused"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/seo-playbook/pause").mock(return_value=httpx.Response(200, json=paused_json))
            result = listings.pause("seo-playbook")
        assert isinstance(result, ListingResponse)
        assert result.status == "paused"

    def test_pause_listing_sends_correct_path(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/my-listing/pause").mock(
                return_value=httpx.Response(200, json={**LISTING_JSON, "status": "paused"})
            )
            listings.pause("my-listing")
        assert route.called


class TestResumeListing:
    def test_resume_listing_returns_active_response(self, listings):
        active_json = {**LISTING_JSON, "status": "active"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings/seo-playbook/resume").mock(return_value=httpx.Response(200, json=active_json))
            result = listings.resume("seo-playbook")
        assert isinstance(result, ListingResponse)
        assert result.status == "active"

    def test_resume_listing_sends_correct_path(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings/my-listing/resume").mock(
                return_value=httpx.Response(200, json={**LISTING_JSON, "status": "active"})
            )
            listings.resume("my-listing")
        assert route.called


class TestDeleteListing:
    def test_delete_listing_sends_delete_request(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/listings/seo-playbook").mock(return_value=httpx.Response(204))
            result = listings.delete("seo-playbook")
        assert route.called
        assert result is None


class TestFulfillmentFields:
    def test_listing_response_managed_fulfillment(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("seo-playbook")
        assert result.fulfillment == "managed"
        assert result.deliverable_type == "file"
        assert result.has_deliverable is True
        assert result.checkout_schema is None

    def test_listing_response_external_fulfillment(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/custom-service").mock(return_value=httpx.Response(200, json=EXTERNAL_LISTING_JSON))
            result = listings.get("custom-service")
        assert result.fulfillment == "external"
        assert result.deliverable_type is None
        assert result.has_deliverable is False
        assert result.checkout_schema is not None
        assert len(result.checkout_schema) == 1
        assert result.checkout_schema[0].name == "shirt_size"
        assert result.checkout_schema[0].type == "select"
        assert result.checkout_schema[0].options == ["S", "M", "L", "XL"]

    def test_listing_response_configure_webhook_action(self, listings):
        json_with_webhook_action = {
            **LISTING_JSON,
            "fulfillment": "external",
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
            mock.get("/v1/listings/ext").mock(return_value=httpx.Response(200, json=json_with_webhook_action))
            result = listings.get("ext")
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
            route = mock.put("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.update("seo-playbook", utm_source="newsletter", utm_campaign="spring-sale")
        body = json.loads(route.calls[0].request.content)
        assert body["utm_source"] == "newsletter"
        assert body["utm_campaign"] == "spring-sale"
        assert "utm_medium" not in body

    def test_listing_response_includes_utm_fields(self, listings):
        listing_with_utm = {**LISTING_JSON, "utm_source": "twitter", "utm_medium": "social", "utm_campaign": "launch"}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=listing_with_utm))
            result = listings.get("seo-playbook")
        assert result.utm_source == "twitter"
        assert result.utm_medium == "social"
        assert result.utm_campaign == "launch"

    def test_listing_response_utm_fields_default_to_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            result = listings.get("seo-playbook")
        assert result.utm_source is None
        assert result.utm_medium is None
        assert result.utm_campaign is None
