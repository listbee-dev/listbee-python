"""Webhooks resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from listbee.types.webhook import WebhookResponse

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
        response = self._client._post("/v1/webhooks", json=body)
        return WebhookResponse.model_validate(response.json())

    def list(self) -> list[WebhookResponse]:
        """Return all webhook endpoints for the account.

        This endpoint returns a plain list (not paginated).

        Returns:
            A list of :class:`~listbee.types.webhook.WebhookResponse` objects.
        """
        response = self._client._get("/v1/webhooks")
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
        response = self._client._put(f"/v1/webhooks/{webhook_id}", json=body)
        return WebhookResponse.model_validate(response.json())

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint.

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").
        """
        self._client._delete(f"/v1/webhooks/{webhook_id}")


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
        response = await self._client._post("/v1/webhooks", json=body)
        return WebhookResponse.model_validate(response.json())

    async def list(self) -> list[WebhookResponse]:
        """Return all webhook endpoints for the account (async).

        This endpoint returns a plain list (not paginated).

        Returns:
            A list of :class:`~listbee.types.webhook.WebhookResponse` objects.
        """
        response = await self._client._get("/v1/webhooks")
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
        response = await self._client._put(f"/v1/webhooks/{webhook_id}", json=body)
        return WebhookResponse.model_validate(response.json())

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint (async).

        Args:
            webhook_id: The webhook's unique identifier (e.g. "wh_3mK8nP2qR5tW7xY1").
        """
        await self._client._delete(f"/v1/webhooks/{webhook_id}")
