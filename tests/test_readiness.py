"""Tests for readiness models and action types."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from listbee.types.shared import (
    AccountReadiness,
    Action,
    ActionCode,
    ActionKind,
    ActionResolve,
    ListingReadiness,
)


class TestActionKind:
    def test_api_value(self):
        assert ActionKind.API == "api"

    def test_human_value(self):
        assert ActionKind.HUMAN == "human"


class TestActionCode:
    def test_stripe_connect_required(self):
        assert ActionCode.STRIPE_CONNECT_REQUIRED == "stripe_connect_required"

    def test_stripe_charges_disabled(self):
        assert ActionCode.STRIPE_CHARGES_DISABLED == "stripe_charges_disabled"

    def test_listing_deliverable_missing(self):
        assert ActionCode.LISTING_DELIVERABLE_MISSING == "listing_deliverable_missing"

    def test_fulfillment_pending(self):
        assert ActionCode.FULFILLMENT_PENDING == "fulfillment_pending"

    def test_otp_verification_pending(self):
        assert ActionCode.OTP_VERIFICATION_PENDING == "otp_verification_pending"


class TestActionResolve:
    def test_api_resolve(self):
        resolve = ActionResolve(
            method="POST",
            endpoint="/v1/account/stripe",
            url=None,
            params={"return_url": "https://example.com"},
        )
        assert resolve.method == "POST"
        assert resolve.endpoint == "/v1/account/stripe"
        assert resolve.url is None
        assert resolve.params == {"return_url": "https://example.com"}

    def test_human_resolve(self):
        resolve = ActionResolve(
            method="GET",
            endpoint=None,
            url="https://dashboard.stripe.com/settings/charges",
            params=None,
        )
        assert resolve.method == "GET"
        assert resolve.url == "https://dashboard.stripe.com/settings/charges"
        assert resolve.endpoint is None
        assert resolve.params is None

    def test_frozen(self):
        resolve = ActionResolve(method="GET", endpoint=None, url="https://example.com", params=None)
        with pytest.raises(ValidationError):
            resolve.method = "POST"  # type: ignore[misc]


class TestAction:
    def test_api_action(self):
        action = Action(
            code=ActionCode.STRIPE_CONNECT_REQUIRED,
            kind=ActionKind.API,
            message="Connect your Stripe account via the API",
            resolve=ActionResolve(
                method="POST",
                endpoint="/v1/account/stripe-connect-session",
                url=None,
                params={"return_url": "https://example.com"},
            ),
        )
        assert action.code == ActionCode.STRIPE_CONNECT_REQUIRED
        assert action.kind == ActionKind.API
        assert action.resolve.endpoint == "/v1/account/stripe-connect-session"

    def test_human_action(self):
        action = Action(
            code=ActionCode.STRIPE_CHARGES_DISABLED,
            kind=ActionKind.HUMAN,
            message="Enable charges in your Stripe dashboard",
            resolve=ActionResolve(
                method="GET",
                endpoint=None,
                url="https://dashboard.stripe.com/settings/charges",
                params=None,
            ),
        )
        assert action.code == ActionCode.STRIPE_CHARGES_DISABLED
        assert action.kind == ActionKind.HUMAN
        assert action.resolve.url == "https://dashboard.stripe.com/settings/charges"

    def test_frozen(self):
        action = Action(
            code=ActionCode.STRIPE_CONNECT_REQUIRED,
            kind=ActionKind.API,
            message="test",
            resolve=ActionResolve(method="POST", endpoint="/v1/account/stripe-connect-session", url=None, params=None),
        )
        with pytest.raises(ValidationError):
            action.code = ActionCode.STRIPE_CHARGES_DISABLED  # type: ignore[misc]


class TestListingReadiness:
    def test_buyable_with_empty_actions(self):
        readiness = ListingReadiness(buyable=True, actions=[], next=None)
        assert readiness.buyable is True
        assert readiness.actions == []
        assert readiness.next is None

    def test_not_buyable_with_actions_and_next(self):
        action = Action(
            code=ActionCode.LISTING_DELIVERABLE_MISSING,
            kind=ActionKind.API,
            message="Attach a deliverable to your listing",
            resolve=ActionResolve(method="PUT", endpoint="/v1/listings/lst_abc123", url=None, params=None),
        )
        readiness = ListingReadiness(buyable=False, actions=[action], next="listing_deliverable_missing")
        assert readiness.buyable is False
        assert len(readiness.actions) == 1
        assert readiness.next == "listing_deliverable_missing"


class TestAccountReadiness:
    def test_operational_with_empty_actions(self):
        readiness = AccountReadiness(operational=True, actions=[], next=None)
        assert readiness.operational is True
        assert readiness.actions == []
        assert readiness.next is None

    def test_not_operational_with_actions_and_next(self):
        action = Action(
            code=ActionCode.STRIPE_CONNECT_REQUIRED,
            kind=ActionKind.HUMAN,
            message="Connect your Stripe account",
            resolve=ActionResolve(
                method="GET",
                endpoint=None,
                url="https://listbee.so/connect/stripe",
                params=None,
            ),
        )
        readiness = AccountReadiness(operational=False, actions=[action], next="stripe_connect_required")
        assert readiness.operational is False
        assert len(readiness.actions) == 1
        assert readiness.next == "stripe_connect_required"


class TestOldBlockerTypesRemoved:
    def test_blocker_code_not_importable(self):
        with pytest.raises(ImportError):
            from listbee.types.shared import BlockerCode  # noqa: F401

    def test_blocker_action_not_importable(self):
        with pytest.raises(ImportError):
            from listbee.types.shared import BlockerAction  # noqa: F401

    def test_blocker_not_importable(self):
        with pytest.raises(ImportError):
            from listbee.types.shared import Blocker  # noqa: F401

    def test_blocker_resolve_not_importable(self):
        with pytest.raises(ImportError):
            from listbee.types.shared import BlockerResolve  # noqa: F401
