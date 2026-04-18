"""Orders resource — sync and async variants."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee._raw_response import RawResponse
from listbee.types.order import OrderResponse, OrderSummary
from listbee.types.order_redeliver import RedeliveryAck

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class _RawOrdersProxy:
    """Proxy that calls Orders methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def get(self, order_id: str) -> RawResponse[OrderResponse]:
        """Retrieve an order by ID and return the raw response."""
        response = self._client.request_raw("GET", f"/v1/orders/{order_id}")
        return RawResponse(response, OrderResponse)

    def fulfill(self, order_id: str) -> RawResponse[OrderResponse]:
        """Fulfill an order and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/orders/{order_id}/fulfill", json={})
        return RawResponse(response, OrderResponse)

    def refund(self, order_id: str) -> RawResponse[OrderResponse]:
        """Issue a refund and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/orders/{order_id}/refund")
        return RawResponse(response, OrderResponse)

    def redeliver(self, order_id: str) -> RawResponse[RedeliveryAck]:
        """Re-queue order webhooks and return the raw response."""
        response = self._client.request_raw("POST", f"/v1/orders/{order_id}/redeliver")
        return RawResponse(response, RedeliveryAck)


class _AsyncRawOrdersProxy:
    """Async proxy that calls Orders methods but returns RawResponse instead of parsed models."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self, order_id: str) -> RawResponse[OrderResponse]:
        """Retrieve an order by ID and return the raw response (async)."""
        response = await self._client.request_raw("GET", f"/v1/orders/{order_id}")
        return RawResponse(response, OrderResponse)

    async def fulfill(self, order_id: str) -> RawResponse[OrderResponse]:
        """Fulfill an order and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/orders/{order_id}/fulfill", json={})
        return RawResponse(response, OrderResponse)

    async def refund(self, order_id: str) -> RawResponse[OrderResponse]:
        """Issue a refund and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/orders/{order_id}/refund")
        return RawResponse(response, OrderResponse)

    async def redeliver(self, order_id: str) -> RawResponse[RedeliveryAck]:
        """Re-queue order webhooks and return the raw response (async)."""
        response = await self._client.request_raw("POST", f"/v1/orders/{order_id}/redeliver")
        return RawResponse(response, RedeliveryAck)


class Orders:
    """Sync resource for the /v1/orders endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _RawOrdersProxy:
        """Access order methods that return raw HTTP responses instead of parsed models."""
        return _RawOrdersProxy(self._client)

    def get(self, order_id: str) -> OrderResponse:
        """Retrieve an order by its ID.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").

        Returns:
            The :class:`~listbee.types.order.OrderResponse` for that order.
        """
        response = self._client.get(f"/v1/orders/{order_id}")
        return OrderResponse.model_validate(response.json())

    def list(
        self,
        *,
        status: str | None = None,
        listing: str | None = None,
        buyer_email: str | None = None,
        created_after: datetime | str | None = None,
        created_before: datetime | str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[OrderSummary]:
        """Return a paginated list of orders.

        Each item is an :class:`~listbee.types.order.OrderSummary` with the core fields
        needed to display order lists. Call :meth:`get` with the order ID for the full
        :class:`~listbee.types.order.OrderResponse` including checkout data and snapshots.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for order in client.orders.list():
                print(order.id)

        Args:
            status: Filter orders by status (e.g. "paid", "fulfilled").
            listing: Filter orders by listing ID.
            buyer_email: Filter orders by buyer email address.
            created_after: Only return orders created after this ISO datetime.
            created_before: Only return orders created before this ISO datetime.
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.order.OrderSummary` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if listing is not None:
            params["listing"] = listing
        if buyer_email is not None:
            params["buyer_email"] = buyer_email
        if created_after is not None:
            params["created_after"] = (
                created_after.isoformat() if isinstance(created_after, datetime) else created_after
            )
        if created_before is not None:
            params["created_before"] = (
                created_before.isoformat() if isinstance(created_before, datetime) else created_before
            )
        if cursor is not None:
            params["cursor"] = cursor
        return self._client.get_page("/v1/orders", params, OrderSummary)

    def fulfill(
        self,
        order_id: str,
        *,
        deliverable: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OrderResponse:
        """Fulfill an order, optionally pushing generated content for ListBee to deliver.

        Call without ``deliverable`` to close out an external fulfillment order.
        Pass ``deliverable`` to push AI-generated or dynamic content for ListBee to deliver
        (async fulfillment mode).

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").
            deliverable: Generated content to deliver to the buyer. Use
                :class:`~listbee.Deliverable` builder:
                ``Deliverable.url("https://...")`` or ``Deliverable.text("...")``.
                Required for ``fulfillment_mode="async"`` listings.
            metadata: Arbitrary key-value pairs to attach to this order.
                Stripe-aligned limits: max 50 keys, keys ≤ 40 chars, string values ≤ 500 chars.

        Returns:
            The fulfilled :class:`~listbee.types.order.OrderResponse`.

        Examples:
            Close out an external fulfillment order::

                order = client.orders.fulfill("ord_9xM4kP7nR2qT5wY1")

            Push AI-generated content::

                from listbee import Deliverable

                order = client.orders.fulfill(
                    "ord_9xM4kP7nR2qT5wY1",
                    deliverable=Deliverable.text("Your personalized report..."),
                )
        """
        body: dict[str, Any] = {}
        if deliverable is not None:
            if hasattr(deliverable, "to_api_body"):
                body["deliverable"] = deliverable.to_api_body()
            else:
                body["deliverable"] = deliverable
        if metadata is not None:
            body["metadata"] = metadata

        response = self._client.post(f"/v1/orders/{order_id}/fulfill", json=body)
        return OrderResponse.model_validate(response.json())

    def refund(self, order_id: str) -> OrderResponse:
        """Issue a full refund for an order.

        Only orders with status 'paid' or 'fulfilled' can be refunded.
        Idempotent — calling on an already-refunded order returns it as-is.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").

        Returns:
            The :class:`~listbee.types.order.OrderResponse`.
        """
        response = self._client.post(f"/v1/orders/{order_id}/refund")
        return OrderResponse.model_validate(response.json())

    def redeliver(self, order_id: str) -> RedeliveryAck:
        """Re-queue ``order.paid`` and ``order.fulfilled`` webhooks for delivery.

        Use when the ``agent_callback_url`` missed a delivery and you need to
        re-trigger fulfillment. Both events are scheduled for immediate re-delivery.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").

        Returns:
            A :class:`~listbee.types.order_redeliver.RedeliveryAck` with
            ``scheduled_attempts`` set to the number of events queued.
        """
        response = self._client.post(f"/v1/orders/{order_id}/redeliver")
        return RedeliveryAck.model_validate(response.json())


class AsyncOrders:
    """Async resource for the /v1/orders endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    @property
    def with_raw_response(self) -> _AsyncRawOrdersProxy:
        """Access order methods that return raw HTTP responses instead of parsed models."""
        return _AsyncRawOrdersProxy(self._client)

    async def get(self, order_id: str) -> OrderResponse:
        """Retrieve an order by its ID (async).

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").

        Returns:
            The :class:`~listbee.types.order.OrderResponse` for that order.
        """
        response = await self._client.get(f"/v1/orders/{order_id}")
        return OrderResponse.model_validate(response.json())

    async def list(
        self,
        *,
        status: str | None = None,
        listing: str | None = None,
        buyer_email: str | None = None,
        created_after: datetime | str | None = None,
        created_before: datetime | str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> AsyncCursorPage[OrderSummary]:
        """Return a paginated list of orders (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for order in await client.orders.list():
                print(order.id)

        Args:
            status: Filter orders by status (e.g. "paid", "fulfilled").
            listing: Filter orders by listing ID.
            buyer_email: Filter orders by buyer email address.
            created_after: Only return orders created after this ISO datetime.
            created_before: Only return orders created before this ISO datetime.
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.order.OrderSummary` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if listing is not None:
            params["listing"] = listing
        if buyer_email is not None:
            params["buyer_email"] = buyer_email
        if created_after is not None:
            params["created_after"] = (
                created_after.isoformat() if isinstance(created_after, datetime) else created_after
            )
        if created_before is not None:
            params["created_before"] = (
                created_before.isoformat() if isinstance(created_before, datetime) else created_before
            )
        if cursor is not None:
            params["cursor"] = cursor
        return await self._client.get_page("/v1/orders", params, OrderSummary)

    async def fulfill(
        self,
        order_id: str,
        *,
        deliverable: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OrderResponse:
        """Fulfill an order, optionally pushing generated content (async).

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").
            deliverable: Generated content to deliver. Use :class:`~listbee.Deliverable`
                builder: ``Deliverable.url(...)`` or ``Deliverable.text(...)``.
            metadata: Arbitrary key-value pairs to attach to this order.

        Returns:
            The fulfilled :class:`~listbee.types.order.OrderResponse`.

        Examples:
            Push AI-generated content::

                from listbee import Deliverable

                order = await client.orders.fulfill(
                    "ord_9xM4kP7nR2qT5wY1",
                    deliverable=Deliverable.text("Your personalized report..."),
                )
        """
        body: dict[str, Any] = {}
        if deliverable is not None:
            if hasattr(deliverable, "to_api_body"):
                body["deliverable"] = deliverable.to_api_body()
            else:
                body["deliverable"] = deliverable
        if metadata is not None:
            body["metadata"] = metadata

        response = await self._client.post(f"/v1/orders/{order_id}/fulfill", json=body)
        return OrderResponse.model_validate(response.json())

    async def refund(self, order_id: str) -> OrderResponse:
        """Issue a full refund for an order (async).

        Only orders with status 'paid' or 'fulfilled' can be refunded.
        Idempotent — calling on an already-refunded order returns it as-is.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").

        Returns:
            The :class:`~listbee.types.order.OrderResponse`.
        """
        response = await self._client.post(f"/v1/orders/{order_id}/refund")
        return OrderResponse.model_validate(response.json())

    async def redeliver(self, order_id: str) -> RedeliveryAck:
        """Re-queue ``order.paid`` and ``order.fulfilled`` webhooks for delivery (async).

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").

        Returns:
            A :class:`~listbee.types.order_redeliver.RedeliveryAck` with
            ``scheduled_attempts`` set to the number of events queued.
        """
        response = await self._client.post(f"/v1/orders/{order_id}/redeliver")
        return RedeliveryAck.model_validate(response.json())
