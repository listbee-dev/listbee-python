"""Tests for the customers resource."""

import httpx
import respx

from listbee._base_client import SyncClient
from listbee.resources.customers import Customers
from listbee.types.customer import CustomerResponse

CUSTOMER_JSON = {
    "object": "customer",
    "id": "cus_7kQ2xY9mN3pR5tW1vB8a01",
    "email": "alice@example.com",
    "total_orders": 3,
    "total_spent": 8700,
    "currency": "usd",
    "first_order_at": "2026-03-15T10:00:00Z",
    "last_order_at": "2026-04-01T14:30:00Z",
    "created_at": "2026-03-15T10:00:00Z",
}

LIST_RESPONSE_JSON = {
    "object": "list",
    "data": [CUSTOMER_JSON],
    "has_more": False,
    "total_count": 1,
    "cursor": None,
}


class TestListCustomers:
    def test_list_customers_returns_page(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/customers").mock(return_value=httpx.Response(200, json=LIST_RESPONSE_JSON))
            page = customers.list()
        assert len(page.data) == 1
        assert isinstance(page.data[0], CustomerResponse)
        assert page.data[0].id == "cus_7kQ2xY9mN3pR5tW1vB8a01"

    def test_list_customers_passes_email_filter(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/customers").mock(return_value=httpx.Response(200, json=LIST_RESPONSE_JSON))
            list(customers.list(email="alice@example.com"))
        assert "email=alice%40example.com" in str(route.calls[0].request.url)

    def test_list_customers_passes_limit_and_cursor(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/customers").mock(return_value=httpx.Response(200, json=LIST_RESPONSE_JSON))
            list(customers.list(limit=5, cursor="cur_abc"))
        url = str(route.calls[0].request.url)
        assert "limit=5" in url
        assert "cursor=cur_abc" in url


class TestGetCustomer:
    def test_get_customer_returns_customer_response(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/customers/cus_7kQ2xY9mN3pR5tW1vB8a01").mock(
                return_value=httpx.Response(200, json=CUSTOMER_JSON)
            )
            result = customers.get("cus_7kQ2xY9mN3pR5tW1vB8a01")
        assert isinstance(result, CustomerResponse)
        assert result.email == "alice@example.com"
        assert result.total_orders == 3
        assert result.total_spent == 8700


class TestGetByEmail:
    def test_returns_customer_when_found(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/customers").mock(return_value=httpx.Response(200, json=LIST_RESPONSE_JSON))
            result = customers.get_by_email("alice@example.com")
        assert isinstance(result, CustomerResponse)
        assert result.email == "alice@example.com"

    def test_returns_none_when_not_found(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        empty_page = {**LIST_RESPONSE_JSON, "data": [], "total_count": 0}
        with respx.mock(base_url="https://api.listbee.so") as mock:
            mock.get("/v1/customers").mock(return_value=httpx.Response(200, json=empty_page))
            result = customers.get_by_email("unknown@example.com")
        assert result is None

    def test_passes_email_and_limit_1_to_list(self):
        client = SyncClient(api_key="lb_test_key_1234567890abcdef")
        customers = Customers(client)
        with respx.mock(base_url="https://api.listbee.so") as mock:
            route = mock.get("/v1/customers").mock(return_value=httpx.Response(200, json=LIST_RESPONSE_JSON))
            customers.get_by_email("alice@example.com")
        url = str(route.calls[0].request.url)
        assert "email=alice%40example.com" in url
        assert "limit=1" in url
