"""Webhooks resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee._pagination import AsyncCursorPage, SyncCursorPage
from listbee.types.webhook import WebhookEventResponse, WebhookResponse, WebhookTestResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Webhooks:
    """Sync resource for the /v1/webhooks endpoint."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(
        self,
        *,
        name: str,
        url: str,
        events: list[str] | None = None,
    ) -> WebhookResponse:
        """Create a new webhook endpoint.

        Args:
            name: Display name for identifying this endpoint.
            url: HTTPS endpoint URL that receives POST requests for each event.
            events: Event types to subscribe to. An empty list (or omitting this
                param) means all events are delivered.

        Returns:
            The created :class:`~listbee.types.webhook.WebhookResponse`.
        """
        body: dict[str, Any] = {"name": name, "url": url}
        if events is not None:
            body["events"] = events
        response = self._client.post("/v1/webhooks", json=body)
        return WebhookResponse.model_validate(response.json())

    def list(self) -> list[WebhookResponse]:
        """Return all webhook endpoints for the account.

        This endpoint returns a plain list (not paginated).

        Returns:
            A list of :class:`~listbee.types.webhook.WebhookResponse` objects.
        """
        response = self._client.get("/v1/webhooks")
        body = response.json()
        # Try "data" key first; fall back to "items" for backwards compat
        items = body.get("data") if body.get("data") is not None else body.get("items", [])
        return [WebhookResponse.model_validate(item) for item in items]

    def update(
        self,
        webhook_id: str,
        *,
        name: str | None = None,
        url: str | None = None,
        events: list[str] | None = None,
        enabled: bool | None = None,
    ) -> WebhookResponse:
        """Update an existing webhook endpoint.

        Only the supplied fields are updated; all others remain unchanged.

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").
            name: New display name.
            url: New HTTPS endpoint URL.
            events: New list of subscribed event types.
            enabled: Pass ``False`` to pause delivery without deleting the endpoint.

        Returns:
            The updated :class:`~listbee.types.webhook.WebhookResponse`.
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if enabled is not None:
            body["enabled"] = enabled
        response = self._client.put(f"/v1/webhooks/{webhook_id}", json=body)
        return WebhookResponse.model_validate(response.json())

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint.

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").
        """
        self._client.delete(f"/v1/webhooks/{webhook_id}")

    def list_events(
        self,
        webhook_id: str,
        *,
        status: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[WebhookEventResponse]:
        """List delivery events for a webhook endpoint.

        Iterating the returned page automatically fetches subsequent pages:

        .. code-block:: python

            for event in client.webhooks.list_events("wh_abc123"):
                print(event.id)

        Args:
            webhook_id: Webhook ID (e.g. "wh_abc123").
            status: Filter by status (``"pending"``, ``"delivered"``, ``"failed"``).
            limit: Results per page (1-100, default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            A :class:`~listbee._pagination.SyncCursorPage` of
            :class:`~listbee.types.webhook.WebhookEventResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        return self._client.get_page(
            path=f"/v1/webhooks/{webhook_id}/events",
            params=params,
            model=WebhookEventResponse,
        )

    def retry_event(self, webhook_id: str, event_id: str) -> WebhookEventResponse:
        """Retry delivery of a failed webhook event.

        Args:
            webhook_id: The webhook's unique identifier.
            event_id: The event's unique identifier.

        Returns:
            The :class:`~listbee.types.webhook.WebhookEventResponse`.
        """
        response = self._client.post(f"/v1/webhooks/{webhook_id}/events/{event_id}/retry")
        return WebhookEventResponse.model_validate(response.json())

    def test(self, webhook_id: str) -> WebhookTestResponse:
        """Send a test event to the webhook endpoint.

        Args:
            webhook_id: The webhook's unique identifier.

        Returns:
            A :class:`~listbee.types.webhook.WebhookTestResponse` with the delivery result.
        """
        response = self._client.post(f"/v1/webhooks/{webhook_id}/test")
        return WebhookTestResponse.model_validate(response.json())

    def retry_failed_events(self, webhook_id: str) -> list[WebhookEventResponse]:
        """Retry all failed events for a webhook endpoint.

        Fetches all events with status ``"failed"`` and retries each one.

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").

        Returns:
            List of retried :class:`~listbee.types.webhook.WebhookEventResponse` objects.
        """
        retried: list[WebhookEventResponse] = []
        for event in self.list_events(webhook_id, status="failed"):
            result = self.retry_event(webhook_id, event.id)
            retried.append(result)
        return retried


class AsyncWebhooks:
    """Async resource for the /v1/webhooks endpoint."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        name: str,
        url: str,
        events: list[str] | None = None,
    ) -> WebhookResponse:
        """Create a new webhook endpoint (async).

        Args:
            name: Display name for identifying this endpoint.
            url: HTTPS endpoint URL that receives POST requests for each event.
            events: Event types to subscribe to. An empty list (or omitting this
                param) means all events are delivered.

        Returns:
            The created :class:`~listbee.types.webhook.WebhookResponse`.
        """
        body: dict[str, Any] = {"name": name, "url": url}
        if events is not None:
            body["events"] = events
        response = await self._client.post("/v1/webhooks", json=body)
        return WebhookResponse.model_validate(response.json())

    async def list(self) -> list[WebhookResponse]:
        """Return all webhook endpoints for the account (async).

        This endpoint returns a plain list (not paginated).

        Returns:
            A list of :class:`~listbee.types.webhook.WebhookResponse` objects.
        """
        response = await self._client.get("/v1/webhooks")
        body = response.json()
        # Try "data" key first; fall back to "items" for backwards compat
        items = body.get("data") if body.get("data") is not None else body.get("items", [])
        return [WebhookResponse.model_validate(item) for item in items]

    async def update(
        self,
        webhook_id: str,
        *,
        name: str | None = None,
        url: str | None = None,
        events: list[str] | None = None,
        enabled: bool | None = None,
    ) -> WebhookResponse:
        """Update an existing webhook endpoint (async).

        Only the supplied fields are updated; all others remain unchanged.

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").
            name: New display name.
            url: New HTTPS endpoint URL.
            events: New list of subscribed event types.
            enabled: Pass ``False`` to pause delivery without deleting the endpoint.

        Returns:
            The updated :class:`~listbee.types.webhook.WebhookResponse`.
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if enabled is not None:
            body["enabled"] = enabled
        response = await self._client.put(f"/v1/webhooks/{webhook_id}", json=body)
        return WebhookResponse.model_validate(response.json())

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint (async).

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").
        """
        await self._client.delete(f"/v1/webhooks/{webhook_id}")

    async def list_events(
        self,
        webhook_id: str,
        *,
        status: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> AsyncCursorPage[WebhookEventResponse]:
        """List delivery events for a webhook endpoint (async).

        Async-iterate the returned page to transparently fetch subsequent pages:

        .. code-block:: python

            async for event in await client.webhooks.list_events("wh_abc123"):
                print(event.id)

        Args:
            webhook_id: Webhook ID (e.g. "wh_abc123").
            status: Filter by status (``"pending"``, ``"delivered"``, ``"failed"``).
            limit: Results per page (1-100, default 20).
            cursor: Pagination cursor from a previous response.

        Returns:
            An :class:`~listbee._pagination.AsyncCursorPage` of
            :class:`~listbee.types.webhook.WebhookEventResponse` objects.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        return await self._client.get_page(
            path=f"/v1/webhooks/{webhook_id}/events",
            params=params,
            model=WebhookEventResponse,
        )

    async def retry_event(self, webhook_id: str, event_id: str) -> WebhookEventResponse:
        """Retry delivery of a failed webhook event (async).

        Args:
            webhook_id: The webhook's unique identifier.
            event_id: The event's unique identifier.

        Returns:
            The :class:`~listbee.types.webhook.WebhookEventResponse`.
        """
        response = await self._client.post(f"/v1/webhooks/{webhook_id}/events/{event_id}/retry")
        return WebhookEventResponse.model_validate(response.json())

    async def test(self, webhook_id: str) -> WebhookTestResponse:
        """Send a test event to the webhook endpoint (async).

        Args:
            webhook_id: The webhook's unique identifier.

        Returns:
            A :class:`~listbee.types.webhook.WebhookTestResponse` with the delivery result.
        """
        response = await self._client.post(f"/v1/webhooks/{webhook_id}/test")
        return WebhookTestResponse.model_validate(response.json())

    async def retry_failed_events(self, webhook_id: str) -> list[WebhookEventResponse]:
        """Retry all failed events for a webhook endpoint (async).

        Fetches all events with status ``"failed"`` and retries each one.

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").

        Returns:
            List of retried :class:`~listbee.types.webhook.WebhookEventResponse` objects.
        """
        retried: list[WebhookEventResponse] = []
        async for event in await self.list_events(webhook_id, status="failed"):
            result = await self.retry_event(webhook_id, event.id)
            retried.append(result)
        return retried
