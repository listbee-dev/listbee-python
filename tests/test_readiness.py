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
    def test_connect_stripe(self):
        assert ActionCode.CONNECT_STRIPE == "connect_stripe"

    def test_enable_charges(self):
        assert ActionCode.ENABLE_CHARGES == "enable_charges"

    def test_update_billing(self):
        assert ActionCode.UPDATE_BILLING == "update_billing"

    def test_attach_deliverable(self):
        assert ActionCode.ATTACH_DELIVERABLE == "attach_deliverable"


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
            code=ActionCode.CONNECT_STRIPE,
            kind=ActionKind.API,
            message="Connect your Stripe account via the API",
            resolve=ActionResolve(
                method="POST",
                endpoint="/v1/account/stripe-connect-session",
                url=None,
                params={"return_url": "https://example.com"},
            ),
        )
        assert action.code == ActionCode.CONNECT_STRIPE
        assert action.kind == ActionKind.API
        assert action.resolve.endpoint == "/v1/account/stripe-connect-session"

    def test_human_action(self):
        action = Action(
            code=ActionCode.ENABLE_CHARGES,
            kind=ActionKind.HUMAN,
            message="Enable charges in your Stripe dashboard",
            resolve=ActionResolve(
                method="GET",
                endpoint=None,
                url="https://dashboard.stripe.com/settings/charges",
                params=None,
            ),
        )
        assert action.code == ActionCode.ENABLE_CHARGES
        assert action.kind == ActionKind.HUMAN
        assert action.resolve.url == "https://dashboard.stripe.com/settings/charges"

    def test_frozen(self):
        action = Action(
            code=ActionCode.CONNECT_STRIPE,
            kind=ActionKind.API,
            message="test",
            resolve=ActionResolve(method="POST", endpoint="/v1/account/stripe-connect-session", url=None, params=None),
        )
        with pytest.raises(ValidationError):
            action.code = ActionCode.ENABLE_CHARGES  # type: ignore[misc]


class TestListingReadiness:
    def test_sellable_with_empty_actions(self):
        readiness = ListingReadiness(sellable=True, actions=[], next=None)
        assert readiness.sellable is True
        assert readiness.actions == []
        assert readiness.next is None

    def test_not_sellable_with_actions_and_next(self):
        action = Action(
            code=ActionCode.ATTACH_DELIVERABLE,
            kind=ActionKind.API,
            message="Attach a deliverable to your listing",
            resolve=ActionResolve(method="POST", endpoint="/v1/listings/slug/deliverables", url=None, params=None),
        )
        readiness = ListingReadiness(sellable=False, actions=[action], next="attach_deliverable")
        assert readiness.sellable is False
        assert len(readiness.actions) == 1
        assert readiness.next == "attach_deliverable"


class TestAccountReadiness:
    def test_operational_with_empty_actions(self):
        readiness = AccountReadiness(operational=True, actions=[], next=None)
        assert readiness.operational is True
        assert readiness.actions == []
        assert readiness.next is None

    def test_not_operational_with_actions_and_next(self):
        action = Action(
            code=ActionCode.CONNECT_STRIPE,
            kind=ActionKind.HUMAN,
            message="Connect your Stripe account",
            resolve=ActionResolve(
                method="GET",
                endpoint=None,
                url="https://listbee.so/connect/stripe",
                params=None,
            ),
        )
        readiness = AccountReadiness(operational=False, actions=[action], next="connect_stripe")
        assert readiness.operational is False
        assert len(readiness.actions) == 1
        assert readiness.next == "connect_stripe"


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
