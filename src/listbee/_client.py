from __future__ import annotations

from typing import Any

from listbee._base_client import AsyncClient, SyncClient
from listbee.resources.account import Account, AsyncAccount
from listbee.resources.listings import AsyncListings, Listings
from listbee.resources.orders import AsyncOrders, Orders
from listbee.resources.webhooks import AsyncWebhooks, Webhooks


class ListBee(SyncClient):
    """Synchronous ListBee API client.

    Usage:
        from listbee import ListBee

        client = ListBee(api_key="lb_...")
        listing = client.listings.create(
            name="SEO Playbook",
            price=2999,
            currency="USD",
            content="https://example.com/ebook.pdf",
        )
        print(listing.url)

    The client reads LISTBEE_API_KEY from the environment if no api_key is provided.
    Use as a context manager to ensure the HTTP connection is closed:

        with ListBee() as client:
            client.listings.list()

    Args:
        api_key: Your ListBee API key (lb_...). Falls back to LISTBEE_API_KEY env var.
        base_url: API base URL. Default: https://api.listbee.so
        timeout: Default request timeout in seconds. Default: 30.0
        max_retries: Max retries on 429/5xx responses. Default: 3
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.listings = Listings(self)
        self.orders = Orders(self)
        self.webhooks = Webhooks(self)
        self.account = Account(self)


class AsyncListBee(AsyncClient):
    """Asynchronous ListBee API client.

    Usage:
        from listbee import AsyncListBee

        client = AsyncListBee(api_key="lb_...")
        listing = await client.listings.create(
            name="SEO Playbook",
            price=2999,
            currency="USD",
            content="https://example.com/ebook.pdf",
        )

    Use as an async context manager:

        async with AsyncListBee() as client:
            await client.listings.list()

    Args:
        api_key: Your ListBee API key (lb_...). Falls back to LISTBEE_API_KEY env var.
        base_url: API base URL. Default: https://api.listbee.so
        timeout: Default request timeout in seconds. Default: 30.0
        max_retries: Max retries on 429/5xx responses. Default: 3
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.listings = AsyncListings(self)
        self.orders = AsyncOrders(self)
        self.webhooks = AsyncWebhooks(self)
        self.account = AsyncAccount(self)
