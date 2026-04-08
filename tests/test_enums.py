"""Tests that SDK enums match the canonical spec exactly."""

from listbee import (
    ActionCode,
    DeliverableStatus,
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
            "customer.created",
        }
        assert {e.value for e in WebhookEventType} == expected

    def test_no_stale_values(self):
        stale = {"order.shipped", "listing.paused", "listing.resumed"}
        current = {e.value for e in WebhookEventType}
        assert stale.isdisjoint(current)


class TestActionCode:
    def test_canonical_values(self):
        expected = {
            "connect_stripe",
            "enable_charges",
            "update_billing",
            "attach_deliverable",
            "configure_webhook",
            "publish_listing",
            "webhook_disabled",
        }
        assert {e.value for e in ActionCode} == expected

    def test_no_stale_values(self):
        assert "set_stripe_key" not in {e.value for e in ActionCode}


class TestDeliverableStatus:
    def test_exists(self):
        assert {e.value for e in DeliverableStatus} == {"processing", "ready", "failed"}
