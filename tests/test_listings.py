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
    "content_type": "file",
    "has_content": True,
    "has_cover": True,
    "compare_at_price": None,
    "badges": [],
    "cover_blur": "auto",
    "rating": None,
    "rating_count": None,
    "reviews": [],
    "faqs": [],
    "metadata": None,
    "status": "active",
    "url": "https://buy.listbee.so/seo-playbook",
    "readiness": {"sellable": True, "actions": [], "next": None},
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
            result = listings.create(
                name="SEO Playbook", price=2999, content="https://example.com/file.pdf"
            )
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
            result = listings.create(name="SEO Playbook", price=2999, content="text content")
        assert result.readiness.sellable is False
        assert len(result.readiness.actions) == 1
        assert result.readiness.actions[0].code == "set_stripe_key"
        assert result.readiness.actions[0].kind == "api"
        assert result.readiness.actions[0].resolve.endpoint == "/v1/account/stripe"
        assert result.readiness.next == "set_stripe_key"

    def test_create_listing_optional_fields_omitted_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="SEO Playbook", price=2999, content="text")
        body = json.loads(route.calls[0].request.content)
        assert "description" not in body
        assert "tagline" not in body
        assert "cover_blur" not in body  # default "auto" is not sent
        assert "currency" not in body  # currency is now on the account

    def test_create_listing_cover_blur_sent_when_not_auto(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, content="text", cover_blur="true")
        body = json.loads(route.calls[0].request.content)
        assert body["cover_blur"] == "true"


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
        assert "currency" not in body
        assert "description" not in body

    def test_update_returns_listing_response(self, listings):
        updated = {**LISTING_JSON, "name": "Updated Name", "price": 3900}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.put("/v1/listings/seo-playbook").mock(return_value=httpx.Response(200, json=updated))
            result = listings.update("seo-playbook", name="Updated Name", price=3900)
        assert isinstance(result, ListingResponse)
        assert result.name == "Updated Name"
        assert result.price == 3900


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
