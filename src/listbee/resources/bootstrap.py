"""Bootstrap resource — sync and async variants."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from listbee.types.bootstrap import BootstrapPollResponse, BootstrapStartResponse, BootstrapVerifyResponse

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient


class Bootstrap:
    """Sync resource for the 2-step bootstrap flow.

    Bootstrap creates a new account and returns an API key in two steps:

    1. :meth:`start` — sends an OTP to the email address, returns a ``bootstrap_token``
    2. :meth:`verify` — verifies the OTP, returns the API key and Stripe onboarding URL
    3. (Optional) :meth:`poll` — poll readiness after Stripe onboarding

    The ``api_key`` in the :class:`~listbee.types.bootstrap.BootstrapVerifyResponse` is only
    returned once. Store it immediately and use it as the Bearer token for all
    subsequent API calls.

    Use the high-level :meth:`run` helper to orchestrate the full flow:

    Example::

        from listbee import ListBee

        client = ListBee(api_key="")

        def on_human_action(url: str) -> str:
            print(f"Complete Stripe onboarding: {url}")
            input("Press Enter when done...")
            return "done"

        api_key = client.bootstrap.run("seller@example.com", on_human_action=on_human_action)
        print(api_key)  # lb_... — save this immediately
    """

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def start(self, *, email: str) -> BootstrapStartResponse:
        """Start the bootstrap flow — sends an OTP to the given email.

        This is step 1. No authentication required.

        Args:
            email: Account owner email address. An OTP will be sent here.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapStartResponse` containing
            the ``bootstrap_token`` (pass to :meth:`verify`) and ``account_id``.
        """
        response = self._client.post("/v1/bootstrap/start", json={"email": email})
        return BootstrapStartResponse.model_validate(response.json())

    def verify(self, *, bootstrap_token: str, otp_code: str) -> BootstrapVerifyResponse:
        """Verify the OTP — creates/confirms the account and returns the API key.

        This is step 2. Pass the ``bootstrap_token`` from :meth:`start` and the
        6-digit OTP code from the email. The ``api_key`` in the response is shown
        **once** — store it immediately.

        Args:
            bootstrap_token: Bootstrap token returned by :meth:`start`.
            otp_code: 6-digit OTP code from the email.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapVerifyResponse` with
            ``api_key``, ``account_id``, ``stripe_onboarding_url``, and ``readiness``.
        """
        response = self._client.post(
            "/v1/bootstrap/verify",
            json={"bootstrap_token": bootstrap_token, "otp_code": otp_code},
        )
        return BootstrapVerifyResponse.model_validate(response.json())

    def poll(self, account_id: str) -> BootstrapPollResponse:
        """Poll account readiness after OTP verification.

        Call after :meth:`verify` to check whether the account is operational.
        Poll periodically until ``ready`` is ``True`` — typically after the user
        completes Stripe Connect onboarding.

        Args:
            account_id: The account ID from :meth:`verify` or :meth:`start`.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapPollResponse` with
            ``ready`` flag and full ``readiness`` state.
        """
        response = self._client.get(f"/v1/bootstrap/{account_id}")
        return BootstrapPollResponse.model_validate(response.json())

    def run(
        self,
        email: str,
        *,
        on_otp: Callable[[], str] | None = None,
        on_human_action: Callable[[str], object] | None = None,
        poll_interval: float = 5.0,
        poll_timeout: float = 300.0,
    ) -> str:
        """End-to-end bootstrap helper — returns the API key.

        Orchestrates the full bootstrap flow:

        1. Calls :meth:`start` to send OTP
        2. Calls ``on_otp()`` to get the 6-digit code from the caller
        3. Calls :meth:`verify` — returns the API key immediately
        4. If ``stripe_onboarding_url`` is present, calls ``on_human_action(url)``
           and polls :meth:`poll` until ready or timeout

        Args:
            email: Account owner email address.
            on_otp: Callback that reads and returns the 6-digit OTP from the user.
                Defaults to ``input("OTP: ")``.
            on_human_action: Callback called with the Stripe onboarding URL.
                Should direct the user to complete onboarding and block until they are done
                (or return immediately and let polling handle readiness).
                If omitted, Stripe onboarding is skipped (useful when already connected).
            poll_interval: Seconds between poll attempts (default 5.0).
            poll_timeout: Maximum seconds to wait for readiness (default 300.0).

        Returns:
            The API key string (``lb_...``).

        Raises:
            TimeoutError: If the account is not ready within ``poll_timeout`` seconds.

        Example::

            api_key = client.bootstrap.run(
                "seller@example.com",
                on_otp=lambda: input("Enter OTP: "),
                on_human_action=lambda url: print(f"Visit: {url}"),
            )
        """
        # Step 1: send OTP
        start_resp = self.start(email=email)

        # Step 2: get OTP from caller
        code = input("Enter the OTP from your email: ").strip() if on_otp is None else on_otp()

        # Step 3: verify OTP
        verify_resp = self.verify(bootstrap_token=start_resp.bootstrap_token, otp_code=code)
        api_key = verify_resp.api_key

        # Step 4: Stripe onboarding + poll if needed
        if verify_resp.stripe_onboarding_url and on_human_action:
            on_human_action(verify_resp.stripe_onboarding_url)

        if not verify_resp.readiness.operational:
            deadline = time.monotonic() + poll_timeout
            while time.monotonic() < deadline:
                poll_resp = self.poll(verify_resp.account_id)
                if poll_resp.ready:
                    break
                time.sleep(poll_interval)
            else:
                raise TimeoutError(
                    f"Account {verify_resp.account_id} was not ready within {poll_timeout}s. "
                    "Check readiness.actions for what's pending."
                )

        return api_key


class AsyncBootstrap:
    """Async resource for the 2-step bootstrap flow.

    Bootstrap creates a new account and returns an API key in two steps:

    1. :meth:`start` — sends an OTP to the email address, returns a ``bootstrap_token``
    2. :meth:`verify` — verifies the OTP, returns the API key and Stripe onboarding URL
    3. (Optional) :meth:`poll` — poll readiness after Stripe onboarding

    Example::

        from listbee import AsyncListBee

        client = AsyncListBee(api_key="")

        start = await client.bootstrap.start(email="seller@example.com")
        result = await client.bootstrap.verify(
            bootstrap_token=start.bootstrap_token,
            otp_code="123456",
        )
        print(result.api_key)  # lb_... — save this immediately
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def start(self, *, email: str) -> BootstrapStartResponse:
        """Start the bootstrap flow — sends an OTP to the given email (async).

        This is step 1. No authentication required.

        Args:
            email: Account owner email address. An OTP will be sent here.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapStartResponse` containing
            the ``bootstrap_token`` and ``account_id``.
        """
        response = await self._client.post("/v1/bootstrap/start", json={"email": email})
        return BootstrapStartResponse.model_validate(response.json())

    async def verify(self, *, bootstrap_token: str, otp_code: str) -> BootstrapVerifyResponse:
        """Verify the OTP — creates/confirms the account and returns the API key (async).

        This is step 2. The ``api_key`` in the response is shown **once** — store it immediately.

        Args:
            bootstrap_token: Bootstrap token returned by :meth:`start`.
            otp_code: 6-digit OTP code from the email.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapVerifyResponse` with
            ``api_key``, ``account_id``, ``stripe_onboarding_url``, and ``readiness``.
        """
        response = await self._client.post(
            "/v1/bootstrap/verify",
            json={"bootstrap_token": bootstrap_token, "otp_code": otp_code},
        )
        return BootstrapVerifyResponse.model_validate(response.json())

    async def poll(self, account_id: str) -> BootstrapPollResponse:
        """Poll account readiness after OTP verification (async).

        Args:
            account_id: The account ID from :meth:`verify` or :meth:`start`.

        Returns:
            A :class:`~listbee.types.bootstrap.BootstrapPollResponse` with
            ``ready`` flag and full ``readiness`` state.
        """
        response = await self._client.get(f"/v1/bootstrap/{account_id}")
        return BootstrapPollResponse.model_validate(response.json())

    async def run(
        self,
        email: str,
        *,
        on_otp: Callable[[], str] | None = None,
        on_human_action: Callable[[str], object] | None = None,
        poll_interval: float = 5.0,
        poll_timeout: float = 300.0,
    ) -> str:
        """End-to-end bootstrap helper — returns the API key (async).

        Orchestrates the full bootstrap flow (async variant of sync :meth:`Bootstrap.run`).

        Args:
            email: Account owner email address.
            on_otp: Callback that reads and returns the 6-digit OTP.
            on_human_action: Callback called with the Stripe onboarding URL.
            poll_interval: Seconds between poll attempts (default 5.0).
            poll_timeout: Maximum seconds to wait for readiness (default 300.0).

        Returns:
            The API key string (``lb_...``).

        Raises:
            TimeoutError: If the account is not ready within ``poll_timeout`` seconds.
        """
        import asyncio

        # Step 1: send OTP
        start_resp = await self.start(email=email)

        # Step 2: get OTP from caller
        code = input("Enter the OTP from your email: ").strip() if on_otp is None else on_otp()

        # Step 3: verify OTP
        verify_resp = await self.verify(bootstrap_token=start_resp.bootstrap_token, otp_code=code)
        api_key = verify_resp.api_key

        # Step 4: Stripe onboarding + poll if needed
        if verify_resp.stripe_onboarding_url and on_human_action:
            on_human_action(verify_resp.stripe_onboarding_url)

        if not verify_resp.readiness.operational:
            deadline = time.monotonic() + poll_timeout
            while time.monotonic() < deadline:
                poll_resp = await self.poll(verify_resp.account_id)
                if poll_resp.ready:
                    break
                await asyncio.sleep(poll_interval)
            else:
                raise TimeoutError(
                    f"Account {verify_resp.account_id} was not ready within {poll_timeout}s. "
                    "Check readiness.actions for what's pending."
                )

        return api_key
