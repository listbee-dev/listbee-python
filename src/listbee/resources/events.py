"""Events resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee._raw_response import RawResponse
from listbee.types.event import EventResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class _RawEventsProxy:
    """Proxy that calls Events methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def list(self, **kwargs: Any) -> RawResponse[Any]:
        """List events and return the raw response."""
        params: dict[str, Any] = {"limit": kwargs.pop("limit", 50)}
        params.update({k: v for k, v in kwargs.items() if v is not None})
        response = self._client.request_raw("GET", "/v1/events", params=params)
        return RawResponse(response, dict)


class _AsyncRawEventsProxy:
    """Async proxy that calls Events methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(self, **kwargs: Any) -> RawResponse[Any]:
        """List events (async) and return the raw response."""
        params: dict[str, Any] = {"limit": kwargs.pop("limit", 50)}
        params.update({k: v for k, v in kwargs.items() if v is not None})
        response = await self._client.request_raw("GET", "/v1/events", params=params)
        return RawResponse(response, dict)


class Events:
    """Sync resource for the /v1/events endpoint.

    The event log provides a cursor-paginated history of all events on
    the account. Use it to reconcile missed webhook deliveries or audit
    what happened on an order or listing.

    Example::

        from listbee import ListBee

        client = ListBee(api_key="lb_...")
        for event in client.events.list(type="order.paid"):
            print(event.id, event.type)
    """

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawEventsProxy:
        """Return a proxy that exposes ``RawResponse`` wrappers for each method."""
        return _RawEventsProxy(self._client)

    def list(
        self,
        *,
        type: str | None = None,
        listing_id: str | None = None,
        order_id: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> SyncCursorPage[EventResponse]:
        """Return a cursor-paginated list of events.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for event in client.events.list(type="order.paid"):
                print(event.id, event.type)

        Args:
            type: Filter to a single event type (e.g. ``"order.paid"``).
            listing_id: Filter to events tied to a specific listing ID.
            order_id: Filter to events tied to a specific order ID.
            cursor: Opaque pagination cursor from a previous response.
            limit: Page size, default 50, max 100.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.event.EventResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if type is not None:
            params["type"] = type
        if listing_id is not None:
            params["listing_id"] = listing_id
        if order_id is not None:
            params["order_id"] = order_id
        if cursor is not None:
            params["cursor"] = cursor
        return self._client.get_page("/v1/events", params, EventResponse)


class AsyncEvents:
    """Async resource for the /v1/events endpoint.

    Example::

        from listbee import AsyncListBee

        client = AsyncListBee(api_key="lb_...")
        async for event in await client.events.list(type="order.paid"):
            print(event.id, event.type)
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawEventsProxy:
        """Return an async proxy that exposes ``RawResponse`` wrappers for each method."""
        return _AsyncRawEventsProxy(self._client)

    async def list(
        self,
        *,
        type: str | None = None,
        listing_id: str | None = None,
        order_id: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> AsyncCursorPage[EventResponse]:
        """Return a cursor-paginated list of events (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for event in await client.events.list(type="order.paid"):
                print(event.id, event.type)

        Args:
            type: Filter to a single event type (e.g. ``"order.paid"``).
            listing_id: Filter to events tied to a specific listing ID.
            order_id: Filter to events tied to a specific order ID.
            cursor: Opaque pagination cursor from a previous response.
            limit: Page size, default 50, max 100.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.event.EventResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if type is not None:
            params["type"] = type
        if listing_id is not None:
            params["listing_id"] = listing_id
        if order_id is not None:
            params["order_id"] = order_id
        if cursor is not None:
            params["cursor"] = cursor
        return await self._client.get_page("/v1/events", params, EventResponse)
