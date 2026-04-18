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


class FieldValidationError:
    """A single per-field validation error from a 422 response.

    Attributes:
        loc: JSON path to the invalid field (e.g. ``["body", "price"]``).
        msg: Human-readable error message.
        type: Pydantic error type code (e.g. ``"value_error"``).
    """

    __slots__ = ("loc", "msg", "type")

    def __init__(self, loc: list[str | int], msg: str, type: str) -> None:
        self.loc = loc
        self.msg = msg
        self.type = type

    def __repr__(self) -> str:
        return f"FieldValidationError(loc={self.loc!r}, msg={self.msg!r})"


class APIStatusError(ListBeeError):
    """Raised when the API returns an error response (4xx/5xx).

    Attributes:
        type: URI identifying the error type (points to docs).
        title: Short, stable label for the error category.
        status: HTTP status code.
        detail: Specific explanation of what went wrong.
        code: Machine-readable error code.
        param: Request field that caused the error, if applicable.
        errors: Per-field validation errors (422 responses only). Empty list otherwise.
        extras: RFC 9457 extension members not covered by the standard fields.
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
        errors: list[FieldValidationError] | None = None,
        extras: dict[str, Any] | None = None,
    ) -> None:
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.code = code
        self.param = param
        self.request_id = request_id
        self.errors: list[FieldValidationError] = errors or []
        self.extras: dict[str, Any] = extras or {}
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
        errors: list[FieldValidationError] | None = None,
        extras: dict[str, Any] | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset: datetime | None = None,
    ) -> None:
        super().__init__(
            type=type,
            title=title,
            status=status,
            detail=detail,
            code=code,
            param=param,
            request_id=request_id,
            errors=errors,
            extras=extras,
        )
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


_KNOWN_FIELDS = {"type", "title", "status", "detail", "code", "param", "errors"}


def _parse_field_errors(raw: list[Any] | None) -> list[FieldValidationError]:
    """Parse per-field validation errors from a 422 response body."""
    if not raw:
        return []
    result: list[FieldValidationError] = []
    for item in raw:
        if isinstance(item, dict):
            result.append(
                FieldValidationError(
                    loc=item.get("loc", []),
                    msg=item.get("msg", ""),
                    type=item.get("type", ""),
                )
            )
    return result


def raise_for_status(status_code: int, body: dict[str, Any], headers: dict[str, str]) -> None:
    """Parse an RFC 9457 error body and raise the appropriate exception."""
    error_type: str = body.get("type", "")
    error_title: str = body.get("title", "")
    error_status: int = body.get("status", status_code)
    error_detail: str = body.get("detail", "")
    error_code: str = body.get("code", "")
    error_param: str | None = body.get("param")
    errors: list[FieldValidationError] = _parse_field_errors(body.get("errors"))

    extras = {k: v for k, v in body.items() if k not in _KNOWN_FIELDS}

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
            errors=errors,
            extras=extras,
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
        "errors": errors,
        "extras": extras,
    }

    if exc_class is not None:
        raise exc_class(**kwargs)

    if status_code >= 500:
        raise InternalServerError(**kwargs)

    raise APIStatusError(**kwargs)
