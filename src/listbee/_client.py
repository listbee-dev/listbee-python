from __future__ import annotations

from typing import Any

from listbee._base_client import AsyncClient, SyncClient
from listbee.resources.account import Account, AsyncAccount
from listbee.resources.bootstrap import AsyncBootstrap, Bootstrap
from listbee.resources.customers import AsyncCustomers, Customers
from listbee.resources.files import AsyncFiles, Files
from listbee.resources.listings import AsyncListings, Listings
from listbee.resources.orders import AsyncOrders, Orders
from listbee.resources.stripe import AsyncStripe, Stripe
from listbee.resources.utility import AsyncUtility, Utility
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
        self.bootstrap = Bootstrap(self)
        self.customers = Customers(self)
        self.files = Files(self)
        self.listings = Listings(self)
        self.orders = Orders(self)
        self.webhooks = Webhooks(self)
        self.account = Account(self)
        self.stripe = Stripe(self)
        self.utility = Utility(self)

    def with_options(
        self,
        *,
        api_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> ListBee:
        """Return a new client with overridden options.

        Args:
            api_key: Override the API key for this client instance.
            timeout: Override the request timeout in seconds.
            max_retries: Override the max retry count.

        Returns:
            A new :class:`ListBee` client with the given options applied.
        """
        return ListBee(
            api_key=api_key or self._api_key,
            base_url=self._base_url,
            timeout=timeout if timeout is not None else self._timeout,
            max_retries=max_retries if max_retries is not None else self._max_retries,
        )


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
        self.bootstrap = AsyncBootstrap(self)
        self.customers = AsyncCustomers(self)
        self.files = AsyncFiles(self)
        self.listings = AsyncListings(self)
        self.orders = AsyncOrders(self)
        self.webhooks = AsyncWebhooks(self)
        self.account = AsyncAccount(self)
        self.stripe = AsyncStripe(self)
        self.utility = AsyncUtility(self)

    def with_options(
        self,
        *,
        api_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> AsyncListBee:
        """Return a new async client with overridden options.

        Args:
            api_key: Override the API key for this client instance.
            timeout: Override the request timeout in seconds.
            max_retries: Override the max retry count.

        Returns:
            A new :class:`AsyncListBee` client with the given options applied.
        """
        return AsyncListBee(
            api_key=api_key or self._api_key,
            base_url=self._base_url,
            timeout=timeout if timeout is not None else self._timeout,
            max_retries=max_retries if max_retries is not None else self._max_retries,
        )
