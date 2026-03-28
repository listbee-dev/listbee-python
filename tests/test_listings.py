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
    "price": 2999,
    "currency": "USD",
    "content_type": "file",
    "has_content": True,
    "has_cover": True,
    "compare_at_price": None,
    "badges": [],
    "cover_blur": "auto",
    "rating": 4.8,
    "rating_count": 100,
    "reviews": [],
    "faqs": [],
    "metadata": None,
    "status": "published",
    "url": "https://buy.listbee.so/seo-playbook",
    "readiness": {"sellable": True, "blockers": []},
    "created_at": "2026-03-28T12:00:00Z",
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
                name="SEO Playbook", price=2999, currency="USD", content="https://example.com/file.pdf"
            )
        assert isinstance(result, ListingResponse)
        assert result.id == "lst_abc123"
        assert result.slug == "seo-playbook"
        assert result.name == "SEO Playbook"
        assert result.price == 2999
        assert result.currency == "USD"

    def test_create_listing_with_readiness_blockers(self, listings):
        json_with_blockers = {
            **LISTING_JSON,
            "readiness": {
                "sellable": False,
                "blockers": [
                    {
                        "code": "payments_not_configured",
                        "message": "Connect a Stripe account to accept payments",
                        "resolve": {
                            "action": "connect_stripe",
                            "url": "https://listbee.so/console/connect/stripe",
                        },
                    }
                ],
            },
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=json_with_blockers))
            result = listings.create(name="SEO Playbook", price=2999, currency="USD", content="text content")
        assert result.readiness.sellable is False
        assert len(result.readiness.blockers) == 1
        assert result.readiness.blockers[0].code == "payments_not_configured"
        assert result.readiness.blockers[0].resolve.action == "connect_stripe"

    def test_create_listing_optional_fields_omitted_when_none(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="SEO Playbook", price=2999, currency="USD", content="text")
        body = json.loads(route.calls[0].request.content)
        assert "description" not in body
        assert "tagline" not in body
        assert "cover_blur" not in body  # default "auto" is not sent

    def test_create_listing_cover_blur_sent_when_not_auto(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.post("/v1/listings").mock(return_value=httpx.Response(200, json=LISTING_JSON))
            listings.create(name="Test", price=100, currency="USD", content="text", cover_blur="true")
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
            "cursor": None,
        }
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/listings").mock(return_value=httpx.Response(200, json=page_json))
            results = list(listings.list())
        assert len(results) == 1
        assert isinstance(results[0], ListingResponse)
        assert results[0].id == "lst_abc123"

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


class TestDeleteListing:
    def test_delete_listing_sends_delete_request(self, listings):
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.delete("/v1/listings/seo-playbook").mock(return_value=httpx.Response(204))
            result = listings.delete("seo-playbook")
        assert route.called
        assert result is None
