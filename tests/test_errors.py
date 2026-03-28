import pytest

from listbee._exceptions import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    ConflictError,
    InternalServerError,
    ListBeeError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    raise_for_status,
)


class TestExceptionHierarchy:
    def test_all_exceptions_inherit_from_listbee_error(self):
        assert issubclass(APIStatusError, ListBeeError)
        assert issubclass(APIConnectionError, ListBeeError)
        assert issubclass(APITimeoutError, ListBeeError)

    def test_status_exceptions_inherit_from_api_status_error(self):
        for exc in [AuthenticationError, NotFoundError, ConflictError, ValidationError, RateLimitError, InternalServerError]:
            assert issubclass(exc, APIStatusError)

    def test_api_status_error_has_rfc_9457_fields(self):
        err = APIStatusError(
            type="https://docs.listbee.so/errors/invalid-request",
            title="Invalid Request",
            status=422,
            detail="Price must be greater than 0",
            code="invalid_price",
            param="price",
        )
        assert err.type == "https://docs.listbee.so/errors/invalid-request"
        assert err.title == "Invalid Request"
        assert err.status == 422
        assert err.detail == "Price must be greater than 0"
        assert err.code == "invalid_price"
        assert err.param == "price"
        assert str(err) == "Price must be greater than 0"


class TestRaiseForStatus:
    def _body(self, **overrides):
        base = {
            "type": "https://docs.listbee.so/errors/invalid-request",
            "title": "Invalid Request",
            "status": 422,
            "detail": "Bad input",
            "code": "invalid_input",
        }
        base.update(overrides)
        return base

    def test_401_raises_authentication_error(self):
        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_status(401, self._body(status=401, detail="Invalid API key", code="invalid_api_key"), {})
        assert exc_info.value.status == 401

    def test_404_raises_not_found_error(self):
        with pytest.raises(NotFoundError):
            raise_for_status(404, self._body(status=404), {})

    def test_409_raises_conflict_error(self):
        with pytest.raises(ConflictError):
            raise_for_status(409, self._body(status=409), {})

    def test_422_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            raise_for_status(422, self._body(param="price"), {})
        assert exc_info.value.param == "price"

    def test_429_raises_rate_limit_error_with_headers(self):
        headers = {
            "x-ratelimit-limit": "60",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1711612800",
        }
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(429, self._body(status=429), headers)
        assert exc_info.value.limit == 60
        assert exc_info.value.remaining == 0
        assert exc_info.value.reset is not None

    def test_429_without_rate_limit_headers(self):
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(429, self._body(status=429), {})
        assert exc_info.value.limit is None

    def test_500_raises_internal_server_error(self):
        with pytest.raises(InternalServerError):
            raise_for_status(500, self._body(status=500), {})

    def test_502_raises_internal_server_error(self):
        with pytest.raises(InternalServerError):
            raise_for_status(502, self._body(status=502), {})

    def test_unknown_4xx_raises_api_status_error(self):
        with pytest.raises(APIStatusError):
            raise_for_status(418, self._body(status=418), {})

    def test_catching_base_class_catches_all(self):
        with pytest.raises(ListBeeError):
            raise_for_status(401, self._body(status=401), {})
