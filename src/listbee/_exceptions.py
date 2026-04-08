from __future__ import annotations

from datetime import datetime
from typing import Any


class ListBeeError(Exception):
    """Base exception for all ListBee SDK errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class APIConnectionError(ListBeeError):
    """Raised when a network error prevents the request from completing."""


class APITimeoutError(ListBeeError):
    """Raised when a request times out."""


class APIStatusError(ListBeeError):
    """Raised when the API returns an error response (4xx/5xx).

    Attributes:
        type: URI identifying the error type (points to docs).
        title: Short, stable label for the error category.
        status: HTTP status code.
        detail: Specific explanation of what went wrong.
        code: Machine-readable error code.
        param: Request field that caused the error, if applicable.
    """

    def __init__(
        self,
        *,
        type: str,
        title: str,
        status: int,
        detail: str,
        code: str,
        param: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.code = code
        self.param = param
        self.request_id = request_id
        super().__init__(detail)


class BadRequestError(APIStatusError):
    """Raised on 400 responses — malformed request."""


class AuthenticationError(APIStatusError):
    """Raised on 401 responses — invalid or missing API key."""


class ForbiddenError(APIStatusError):
    """Raised on 403 responses — insufficient permissions."""


class NotFoundError(APIStatusError):
    """Raised on 404 responses — resource not found."""


class ConflictError(APIStatusError):
    """Raised on 409 responses — resource conflict."""


class ValidationError(APIStatusError):
    """Raised on 422 responses — request validation failed."""


class RateLimitError(APIStatusError):
    """Raised on 429 responses — rate limit exceeded.

    Additional attributes parsed from response headers:
        limit: Max requests per window.
        remaining: Requests remaining in current window.
        reset: When the current window resets.
    """

    def __init__(
        self,
        *,
        type: str,
        title: str,
        status: int,
        detail: str,
        code: str,
        param: str | None = None,
        request_id: str | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset: datetime | None = None,
    ) -> None:
        super().__init__(type=type, title=title, status=status, detail=detail, code=code, param=param, request_id=request_id)
        self.limit = limit
        self.remaining = remaining
        self.reset = reset


class InternalServerError(APIStatusError):
    """Raised on 500+ responses — server-side error."""


class PayloadTooLargeError(APIStatusError):
    """Raised on 413 responses — request body too large."""


class WebhookVerificationError(ListBeeError):
    """Raised when webhook signature verification fails."""


class PartialCreationError(ListBeeError):
    """Raised when create_complete creates the listing but fails during file upload or deliverable attachment.

    The ``listing_id`` attribute contains the draft that was created, so the
    caller can resume with individual ``add_deliverable`` calls.
    """

    def __init__(self, listing_id: str, message: str) -> None:
        super().__init__(message)
        self.listing_id = listing_id


STATUS_CODE_TO_EXCEPTION: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    413: PayloadTooLargeError,
    422: ValidationError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: dict[str, Any], headers: dict[str, str]) -> None:
    """Parse an RFC 9457 error body and raise the appropriate exception."""
    error_type: str = body.get("type", "")
    error_title: str = body.get("title", "")
    error_status: int = body.get("status", status_code)
    error_detail: str = body.get("detail", "")
    error_code: str = body.get("code", "")
    error_param: str | None = body.get("param")

    request_id: str | None = headers.get("x-request-id")
    exc_class = STATUS_CODE_TO_EXCEPTION.get(status_code)

    if exc_class is RateLimitError:
        limit_str = headers.get("x-ratelimit-limit")
        remaining_str = headers.get("x-ratelimit-remaining")
        reset_str = headers.get("x-ratelimit-reset")

        raise RateLimitError(
            type=error_type,
            title=error_title,
            status=error_status,
            detail=error_detail,
            code=error_code,
            param=error_param,
            request_id=request_id,
            limit=int(limit_str) if limit_str else None,
            remaining=int(remaining_str) if remaining_str else None,
            reset=datetime.fromtimestamp(float(reset_str)) if reset_str else None,
        )

    kwargs: dict[str, Any] = {
        "type": error_type,
        "title": error_title,
        "status": error_status,
        "detail": error_detail,
        "code": error_code,
        "param": error_param,
        "request_id": request_id,
    }

    if exc_class is not None:
        raise exc_class(**kwargs)

    if status_code >= 500:
        raise InternalServerError(**kwargs)

    raise APIStatusError(**kwargs)
