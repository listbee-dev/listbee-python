"""ListBee Python SDK — DEPRECATED.

ListBee has pivoted to MCP-native architecture. This SDK is no longer
maintained. Use https://mcp.listbee.so or the OpenAPI spec at
https://listbee.so/openapi.json.
"""

import warnings

warnings.warn(
    "listbee Python SDK is deprecated — use MCP (https://mcp.listbee.so) or "
    "OpenAPI (https://listbee.so/openapi.json) directly. See README for details.",
    DeprecationWarning,
    stacklevel=2,
)

# --- existing module content preserved below ---
# ruff: noqa: E402

from httpx import AsyncClient as DefaultAsyncHttpxClient
from httpx import Client as DefaultHttpxClient

from listbee._client import AsyncListBee, ListBee
from listbee._exceptions import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    FieldValidationError,
    ForbiddenError,
    InternalServerError,
    ListBeeError,
    NotFoundError,
    PartialCreationError,
    PayloadTooLargeError,
    RateLimitError,
    ValidationError,
    WebhookVerificationError,
)
from listbee.checkout_field import CheckoutField
from listbee.deliverable import Deliverable
from listbee.helpers import (
    ParsedWebhookEvent,
    format_price,
    from_minor,
    parse_webhook_event,
    resolve_action,
    resolve_action_async,
    to_minor,
)
from listbee.types import (
    AccountReadiness,
    AccountResponse,
    Action,
    ActionCode,
    ActionKind,
    ActionPriority,
    ActionResolve,
    ApiKeyResponse,
    BootstrapCompleteResponse,
    BootstrapPollResponse,
    BootstrapResponse,
    BootstrapStartResponse,
    BootstrapVerifyResponse,
    CheckoutFieldResponse,
    CheckoutFieldType,
    CursorPage,
    DeliverableRequest,
    DeliverableResponse,
    DeliverableType,
    EventResponse,
    FaqItem,
    FulfillmentMode,
    ListingBase,
    ListingCreateResponse,
    ListingDetailResponse,
    ListingReadiness,
    ListingStats,
    ListingStatus,
    ListingSummary,
    OrderReadiness,
    OrderResponse,
    OrderStatus,
    OrderSummary,
    PaymentStatus,
    PlanListResponse,
    RedeliveryAck,
    Review,
    RotateSigningSecretResponse,
    StripeConnectSessionResponse,
    WebhookEventType,
)
from listbee.webhooks import verify_signature

__all__ = [
    "DefaultHttpxClient",
    "DefaultAsyncHttpxClient",
    "Deliverable",
    "CheckoutField",
    "ListBee",
    "AsyncListBee",
    "ListBeeError",
    "APIStatusError",
    "APIConnectionError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "PayloadTooLargeError",
    "ValidationError",
    "RateLimitError",
    "InternalServerError",
    "PartialCreationError",
    "WebhookVerificationError",
    "FieldValidationError",
    "verify_signature",
    "format_price",
    "to_minor",
    "from_minor",
    "resolve_action",
    "resolve_action_async",
    "parse_webhook_event",
    "ParsedWebhookEvent",
    # Enums
    "ActionCode",
    "ActionKind",
    "ActionPriority",
    "CheckoutFieldType",
    "DeliverableType",
    "FulfillmentMode",
    "ListingStatus",
    "OrderStatus",
    "PaymentStatus",
    "WebhookEventType",
    # Readiness models
    "AccountReadiness",
    "Action",
    "ActionResolve",
    "ListingReadiness",
    "OrderReadiness",
    # Response models
    "AccountResponse",
    "ApiKeyResponse",
    "BootstrapStartResponse",
    "BootstrapVerifyResponse",
    "BootstrapPollResponse",
    "BootstrapResponse",
    "BootstrapCompleteResponse",
    "CheckoutFieldResponse",
    "CursorPage",
    "DeliverableRequest",
    "DeliverableResponse",
    "EventResponse",
    "FaqItem",
    "ListingBase",
    "ListingCreateResponse",
    "ListingDetailResponse",
    "ListingStats",
    "ListingSummary",
    "OrderResponse",
    "OrderSummary",
    "PlanListResponse",
    "RedeliveryAck",
    "Review",
    "RotateSigningSecretResponse",
    "StripeConnectSessionResponse",
]
