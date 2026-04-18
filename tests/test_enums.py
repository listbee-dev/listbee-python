"""Tests that SDK enums match the canonical spec exactly."""

from listbee import (
    ActionCode,
    DeliverableType,
    WebhookEventType,
)


class TestWebhookEventType:
    def test_canonical_values(self):
        expected = {
            "order.paid",
            "order.fulfilled",
            "order.refunded",
            "order.disputed",
            "order.dispute_closed",
            "order.canceled",
            "listing.created",
            "listing.updated",
            "listing.published",
            "listing.out_of_stock",
            "listing.deleted",
        }
        assert {e.value for e in WebhookEventType} == expected

    def test_no_stale_values(self):
        stale = {"order.shipped", "listing.paused", "listing.resumed", "customer.created"}
        current = {e.value for e in WebhookEventType}
        assert stale.isdisjoint(current)


class TestActionCode:
    def test_canonical_values(self):
        expected = {
            "otp_verification_pending",
            "stripe_connect_required",
            "stripe_charges_disabled",
            "account_deleted",
            "listing_unpublished",
            "listing_deliverable_missing",
            "fulfillment_pending",
            "dispute_open",
        }
        assert {e.value for e in ActionCode} == expected

    def test_no_stale_values(self):
        stale = {
            "connect_stripe",
            "enable_charges",
            "update_billing",
            "attach_deliverable",
            "configure_webhook",
            "publish_listing",
            "webhook_disabled",
            "set_stripe_key",
        }
        current = {e.value for e in ActionCode}
        assert stale.isdisjoint(current)


class TestDeliverableType:
    def test_exists(self):
        assert {e.value for e in DeliverableType} == {"url", "text"}
