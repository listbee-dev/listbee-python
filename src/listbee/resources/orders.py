"""Orders resource — sync and async variants."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee.types.order import OrderResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Orders:
    """Sync resource for the /v1/orders endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

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
        created_after: datetime | str | None = None,
        created_before: datetime | str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[OrderResponse]:
        """Return a paginated list of orders.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for order in client.orders.list():
                print(order.id)

        Args:
            status: Filter orders by status (e.g. "paid", "fulfilled").
            listing: Filter orders by listing slug (e.g. "seo-playbook").
            created_after: Only return orders created after this ISO datetime.
            created_before: Only return orders created before this ISO datetime.
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.order.OrderResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if listing is not None:
            params["listing"] = listing
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
        return self._client.get_page("/v1/orders", params, OrderResponse)

    def deliver(
        self,
        order_id: str,
        *,
        deliverables: list[dict[str, Any]],
    ) -> OrderResponse:
        """Deliver an order by pushing deliverables for ListBee to deliver.

        Each deliverable dict has ``type`` ('file', 'url', 'text') and either
        ``token`` (for files) or ``value`` (for urls/text). Max 3 items.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").
            deliverables: Array of deliverable dicts to attach.

        Returns:
            The delivered :class:`~listbee.types.order.OrderResponse`.
        """
        body: dict[str, Any] = {"deliverables": deliverables}
        response = self._client.post(f"/v1/orders/{order_id}/deliver", json=body)
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

    def ship(
        self,
        order_id: str,
        *,
        carrier: str,
        tracking_code: str,
        seller_note: str | None = None,
    ) -> OrderResponse:
        """Mark an order as shipped with tracking information.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").
            carrier: Shipping carrier name (e.g. "USPS", "FedEx").
            tracking_code: Shipment tracking code.
            seller_note: Optional note to the buyer.

        Returns:
            The shipped :class:`~listbee.types.order.OrderResponse`.
        """
        body: dict[str, Any] = {
            "carrier": carrier,
            "tracking_code": tracking_code,
        }
        if seller_note is not None:
            body["seller_note"] = seller_note
        response = self._client.post(f"/v1/orders/{order_id}/ship", json=body)
        return OrderResponse.model_validate(response.json())


class AsyncOrders:
    """Async resource for the /v1/orders endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

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
        created_after: datetime | str | None = None,
        created_before: datetime | str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> AsyncCursorPage[OrderResponse]:
        """Return a paginated list of orders (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for order in await client.orders.list():
                print(order.id)

        Args:
            status: Filter orders by status (e.g. "paid", "fulfilled").
            listing: Filter orders by listing slug (e.g. "seo-playbook").
            created_after: Only return orders created after this ISO datetime.
            created_before: Only return orders created before this ISO datetime.
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.order.OrderResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if listing is not None:
            params["listing"] = listing
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
        return await self._client.get_page("/v1/orders", params, OrderResponse)

    async def deliver(
        self,
        order_id: str,
        *,
        deliverables: list[dict[str, Any]],
    ) -> OrderResponse:
        """Deliver an order by pushing deliverables for ListBee to deliver (async).

        Each deliverable dict has ``type`` ('file', 'url', 'text') and either
        ``token`` (for files) or ``value`` (for urls/text). Max 3 items.

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").
            deliverables: Array of deliverable dicts to attach.

        Returns:
            The delivered :class:`~listbee.types.order.OrderResponse`.
        """
        body: dict[str, Any] = {"deliverables": deliverables}
        response = await self._client.post(f"/v1/orders/{order_id}/deliver", json=body)
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

    async def ship(
        self,
        order_id: str,
        *,
        carrier: str,
        tracking_code: str,
        seller_note: str | None = None,
    ) -> OrderResponse:
        """Mark an order as shipped with tracking information (async).

        Args:
            order_id: The order's unique identifier (e.g. "ord_9xM4kP7nR2qT5wY1").
            carrier: Shipping carrier name (e.g. "USPS", "FedEx").
            tracking_code: Shipment tracking code.
            seller_note: Optional note to the buyer.

        Returns:
            The shipped :class:`~listbee.types.order.OrderResponse`.
        """
        body: dict[str, Any] = {
            "carrier": carrier,
            "tracking_code": tracking_code,
        }
        if seller_note is not None:
            body["seller_note"] = seller_note
        response = await self._client.post(f"/v1/orders/{order_id}/ship", json=body)
        return OrderResponse.model_validate(response.json())
