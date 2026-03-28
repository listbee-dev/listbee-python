"""Orders resource — sync and async variants."""

from __future__ import annotations

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
        response = self._client._get(f"/v1/orders/{order_id}")
        return OrderResponse.model_validate(response.json())

    def list(
        self,
        *,
        status: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[OrderResponse]:
        """Return a paginated list of orders.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for order in client.orders.list():
                print(order.id)

        Args:
            status: Filter orders by fulfillment status (e.g. "completed").
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.order.OrderResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        return self._client._get_page("/v1/orders", params, OrderResponse)


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
        response = await self._client._get(f"/v1/orders/{order_id}")
        return OrderResponse.model_validate(response.json())

    async def list(
        self,
        *,
        status: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> AsyncCursorPage[OrderResponse]:
        """Return a paginated list of orders (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for order in await client.orders.list():
                print(order.id)

        Args:
            status: Filter orders by fulfillment status (e.g. "completed").
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.order.OrderResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        return await self._client._get_page("/v1/orders", params, OrderResponse)
