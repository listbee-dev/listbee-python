"""Bootstrap resource — sync and async variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from listbee.types.bootstrap import BootstrapCompleteResponse, BootstrapResponse, BootstrapVerifyResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Bootstrap:
    """Sync resource for the bootstrap flow.

    Bootstrap is a 3-step flow to create an account and obtain an API key:

    1. ``start(email)`` — sends an OTP to the email address, returns a session ID
    2. ``verify(session, code)`` — verifies the OTP, returns a verified session ID
    3. ``complete(session)`` — creates the account and returns the API key (shown once)

    The ``api_key`` in the :class:`~listbee.types.bootstrap.BootstrapCompleteResponse` is only
    returned once. Store it immediately and use it as the Bearer token for all
    subsequent API calls.

    Example::

        from listbee import ListBee

        # No API key needed for bootstrap
        client = ListBee(api_key="")

        session = client.bootstrap.start(email="seller@example.com")
        verified = client.bootstrap.verify(session=session.session, code="123456")
        result = client.bootstrap.complete(session=verified.session)
        print(result.api_key)  # lb_... — save this immediately
    """

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def start(self, *, email: str) -> BootstrapResponse:
        """Start the bootstrap flow — sends an OTP to the given email.

        This is step 1 of 3. No authentication required.

        Args:
            email: Account owner email address. An OTP will be sent here.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapResponse` containing
            the session ID and confirmation that the OTP was sent.
        """
        response = self._client.post("/v1/bootstrap", json={"email": email})
        return BootstrapResponse.model_validate(response.json())

    def verify(self, *, session: str, code: str) -> BootstrapVerifyResponse:
        """Verify the OTP — confirms identity.

        This is step 2 of 3. Pass the session ID from ``start()`` and the
        6-digit OTP code from the email.

        Args:
            session: Session ID returned by :meth:`start`.
            code: 6-digit OTP code from the email.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapVerifyResponse` with
            a verified session ID to pass to :meth:`complete`.
        """
        response = self._client.post(
            "/v1/bootstrap/verify",
            json={"session": session, "code": code},
        )
        return BootstrapVerifyResponse.model_validate(response.json())

    def complete(self, *, session: str) -> BootstrapCompleteResponse:
        """Complete bootstrap — creates the account and returns the API key.

        This is step 3 of 3. The ``api_key`` in the response is shown **once** —
        store it immediately and use it as the Bearer token for all future API calls.

        Args:
            session: Verified session ID from :meth:`verify`.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapCompleteResponse` with
            ``account_id`` and ``api_key`` set.
        """
        response = self._client.post(
            "/v1/bootstrap/complete",
            json={"session": session},
        )
        return BootstrapCompleteResponse.model_validate(response.json())


class AsyncBootstrap:
    """Async resource for the bootstrap flow.

    Bootstrap is a 3-step flow to create an account and obtain an API key:

    1. ``start(email)`` — sends an OTP to the email address, returns a session ID
    2. ``verify(session, code)`` — verifies the OTP, returns a verified session ID
    3. ``complete(session)`` — creates the account and returns the API key (shown once)

    Example::

        from listbee import AsyncListBee

        client = AsyncListBee(api_key="")

        session = await client.bootstrap.start(email="seller@example.com")
        verified = await client.bootstrap.verify(session=session.session, code="123456")
        result = await client.bootstrap.complete(session=verified.session)
        print(result.api_key)  # lb_... — save this immediately
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def start(self, *, email: str) -> BootstrapResponse:
        """Start the bootstrap flow — sends an OTP to the given email (async).

        This is step 1 of 3. No authentication required.

        Args:
            email: Account owner email address. An OTP will be sent here.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapResponse` containing
            the session ID and confirmation that the OTP was sent.
        """
        response = await self._client.post("/v1/bootstrap", json={"email": email})
        return BootstrapResponse.model_validate(response.json())

    async def verify(self, *, session: str, code: str) -> BootstrapVerifyResponse:
        """Verify the OTP — confirms identity (async).

        This is step 2 of 3.

        Args:
            session: Session ID returned by :meth:`start`.
            code: 6-digit OTP code from the email.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapVerifyResponse` with
            a verified session ID to pass to :meth:`complete`.
        """
        response = await self._client.post(
            "/v1/bootstrap/verify",
            json={"session": session, "code": code},
        )
        return BootstrapVerifyResponse.model_validate(response.json())

    async def complete(self, *, session: str) -> BootstrapCompleteResponse:
        """Complete bootstrap — creates the account and returns the API key (async).

        This is step 3 of 3. The ``api_key`` in the response is shown **once** —
        store it immediately and use it as the Bearer token for all future API calls.

        Args:
            session: Verified session ID from :meth:`verify`.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapCompleteResponse` with
            ``account_id`` and ``api_key`` set.
        """
        response = await self._client.post(
            "/v1/bootstrap/complete",
            json={"session": session},
        )
        return BootstrapCompleteResponse.model_validate(response.json())
