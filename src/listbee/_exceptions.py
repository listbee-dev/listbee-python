from __future__ import annotations

from datetime import datetime


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
    ) -> None:
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.code = code
        self.param = param
        super().__init__(detail)


class AuthenticationError(APIStatusError):
    """Raised on 401 responses — invalid or missing API key."""


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
        limit: int | None = None,
        remaining: int | None = None,
        reset: datetime | None = None,
    ) -> None:
        super().__init__(type=type, title=title, status=status, detail=detail, code=code, param=param)
        self.limit = limit
        self.remaining = remaining
        self.reset = reset


class InternalServerError(APIStatusError):
    """Raised on 500+ responses — server-side error."""


class WebhookVerificationError(ListBeeError):
    """Raised when webhook signature verification fails."""


STATUS_CODE_TO_EXCEPTION: dict[int, type[APIStatusError]] = {
    401: AuthenticationError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: dict, headers: dict[str, str]) -> None:
    """Parse an RFC 9457 error body and raise the appropriate exception."""
    kwargs = {
        "type": body.get("type", ""),
        "title": body.get("title", ""),
        "status": body.get("status", status_code),
        "detail": body.get("detail", ""),
        "code": body.get("code", ""),
        "param": body.get("param"),
    }

    exc_class = STATUS_CODE_TO_EXCEPTION.get(status_code)

    if exc_class is RateLimitError:
        limit_str = headers.get("x-ratelimit-limit")
        remaining_str = headers.get("x-ratelimit-remaining")
        reset_str = headers.get("x-ratelimit-reset")

        kwargs["limit"] = int(limit_str) if limit_str else None
        kwargs["remaining"] = int(remaining_str) if remaining_str else None
        kwargs["reset"] = datetime.fromtimestamp(float(reset_str)) if reset_str else None
        raise RateLimitError(**kwargs)

    if exc_class is not None:
        raise exc_class(**kwargs)

    if status_code >= 500:
        raise InternalServerError(**kwargs)

    raise APIStatusError(**kwargs)
