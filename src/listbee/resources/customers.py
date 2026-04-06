"""Customers resource — sync and async variants."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee.types.customer import CustomerResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Customers:
    """Sync resource for the /v1/customers endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def list(
        self,
        *,
        email: str | None = None,
        created_after: datetime | str | None = None,
        created_before: datetime | str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[CustomerResponse]:
        """Return a paginated list of customers.

        Customers are auto-created when a buyer completes their first order.

        Args:
            email: Filter by exact buyer email address.
            created_after: Only customers created after this ISO datetime.
            created_before: Only customers created before this ISO datetime.
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.customer.CustomerResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if email is not None:
            params["email"] = email
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
        return self._client.get_page("/v1/customers", params, CustomerResponse)

    def get(self, customer_id: str) -> CustomerResponse:
        """Retrieve a customer by ID.

        Args:
            customer_id: The customer's unique identifier (e.g. "cus_7kQ2xY9mN3pR5tW1vB8a01").

        Returns:
            The :class:`~listbee.types.customer.CustomerResponse`.
        """
        response = self._client.get(f"/v1/customers/{customer_id}")
        return CustomerResponse.model_validate(response.json())


class AsyncCustomers:
    """Async resource for the /v1/customers endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        email: str | None = None,
        created_after: datetime | str | None = None,
        created_before: datetime | str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> AsyncCursorPage[CustomerResponse]:
        """Return a paginated list of customers (async).

        Args:
            email: Filter by exact buyer email address.
            created_after: Only customers created after this ISO datetime.
            created_before: Only customers created before this ISO datetime.
            limit: Maximum number of items per page (default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.customer.CustomerResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if email is not None:
            params["email"] = email
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
        return await self._client.get_page("/v1/customers", params, CustomerResponse)

    async def get(self, customer_id: str) -> CustomerResponse:
        """Retrieve a customer by ID (async).

        Args:
            customer_id: The customer's unique identifier (e.g. "cus_7kQ2xY9mN3pR5tW1vB8a01").

        Returns:
            The :class:`~listbee.types.customer.CustomerResponse`.
        """
        response = await self._client.get(f"/v1/customers/{customer_id}")
        return CustomerResponse.model_validate(response.json())
