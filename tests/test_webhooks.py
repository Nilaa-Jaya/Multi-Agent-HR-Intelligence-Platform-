"""
Comprehensive tests for webhook system
"""

import pytest
import json
import hmac
import hashlib
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.database.models import Webhook, WebhookDelivery
from src.database.webhook_queries import WebhookQueries
from src.api.webhook_delivery import (
    generate_webhook_signature,
    verify_webhook_signature,
    deliver_webhook,
)
from src.api.webhook_events import (
    WebhookEvents,
    create_webhook_payload,
    create_query_created_payload,
    create_query_escalated_payload,
)


class TestWebhookQueries:
    """Test webhook database operations"""

    def test_create_webhook(self, db_session):
        """Test webhook creation with auto-generated UUID and secret"""
        webhook = WebhookQueries.create_webhook(
            db=db_session,
            url="https://example.com/webhook",
            events=["query.created", "query.escalated"],
        )

        assert webhook is not None
        assert len(webhook.id) == 36  # UUID length
        assert webhook.url == "https://example.com/webhook"
        assert webhook.events == ["query.created", "query.escalated"]
        assert len(webhook.secret_key) > 20  # Auto-generated secret
        assert webhook.is_active is True
        assert webhook.delivery_count == 0
        assert webhook.failure_count == 0

    def test_get_webhook(self, db_session):
        """Test retrieving webhook by ID"""
        webhook = WebhookQueries.create_webhook(
            db=db_session, url="https://example.com/webhook", events=["query.created"]
        )

        retrieved = WebhookQueries.get_webhook(db=db_session, webhook_id=webhook.id)

        assert retrieved is not None
        assert retrieved.id == webhook.id
        assert retrieved.url == webhook.url

    def test_list_webhooks(self, db_session):
        """Test listing webhooks with pagination"""
        # Create multiple webhooks
        for i in range(5):
            WebhookQueries.create_webhook(
                db=db_session,
                url=f"https://example.com/webhook{i}",
                events=["query.created"],
            )

        webhooks = WebhookQueries.list_webhooks(db=db_session, skip=0, limit=3)

        assert len(webhooks) == 3

    def test_list_webhooks_filter_active(self, db_session):
        """Test filtering webhooks by active status"""
        # Create active and inactive webhooks
        active = WebhookQueries.create_webhook(
            db=db_session, url="https://example.com/active", events=["query.created"]
        )

        inactive = WebhookQueries.create_webhook(
            db=db_session, url="https://example.com/inactive", events=["query.created"]
        )
        WebhookQueries.update_webhook(
            db=db_session, webhook_id=inactive.id, is_active=False
        )

        active_webhooks = WebhookQueries.list_webhooks(
            db=db_session, is_active=True
        )

        assert len(active_webhooks) >= 1
        assert all(w.is_active for w in active_webhooks)

    def test_update_webhook(self, db_session):
        """Test updating webhook properties"""
        webhook = WebhookQueries.create_webhook(
            db=db_session, url="https://example.com/webhook", events=["query.created"]
        )

        updated = WebhookQueries.update_webhook(
            db=db_session,
            webhook_id=webhook.id,
            url="https://example.com/new-webhook",
            events=["query.created", "query.escalated"],
            is_active=False,
        )

        assert updated.url == "https://example.com/new-webhook"
        assert updated.events == ["query.created", "query.escalated"]
        assert updated.is_active is False

    def test_delete_webhook(self, db_session):
        """Test deleting webhook"""
        webhook = WebhookQueries.create_webhook(
            db=db_session, url="https://example.com/webhook", events=["query.created"]
        )

        deleted = WebhookQueries.delete_webhook(
            db=db_session, webhook_id=webhook.id
        )

        assert deleted is True

        retrieved = WebhookQueries.get_webhook(db=db_session, webhook_id=webhook.id)
        assert retrieved is None

    def test_get_active_webhooks_for_event(self, db_session):
        """Test retrieving active webhooks subscribed to specific event"""
        # Create webhooks with different events
        webhook1 = WebhookQueries.create_webhook(
            db=db_session,
            url="https://example.com/webhook1",
            events=["query.created", "query.escalated"],
        )

        webhook2 = WebhookQueries.create_webhook(
            db=db_session,
            url="https://example.com/webhook2",
            events=["query.created"],
        )

        webhook3 = WebhookQueries.create_webhook(
            db=db_session,
            url="https://example.com/webhook3",
            events=["feedback.received"],
        )

        # Get webhooks for query.created event
        webhooks = WebhookQueries.get_active_webhooks_for_event(
            db=db_session, event_type="query.created"
        )

        webhook_ids = [w.id for w in webhooks]
        assert webhook1.id in webhook_ids
        assert webhook2.id in webhook_ids
        assert webhook3.id not in webhook_ids

    def test_update_delivery_stats(self, db_session):
        """Test updating webhook delivery statistics"""
        webhook = WebhookQueries.create_webhook(
            db=db_session, url="https://example.com/webhook", events=["query.created"]
        )

        # Update success stats
        WebhookQueries.update_delivery_stats(
            db=db_session, webhook_id=webhook.id, success=True
        )

        updated = WebhookQueries.get_webhook(db=db_session, webhook_id=webhook.id)
        assert updated.delivery_count == 1
        assert updated.failure_count == 0
        assert updated.last_delivery_at is not None

        # Update failure stats
        WebhookQueries.update_delivery_stats(
            db=db_session, webhook_id=webhook.id, success=False
        )

        updated = WebhookQueries.get_webhook(db=db_session, webhook_id=webhook.id)
        assert updated.delivery_count == 2  # Both success and failure count as deliveries
        assert updated.failure_count == 1
        assert updated.last_failure_at is not None


class TestWebhookSignatures:
    """Test webhook signature generation and verification"""

    def test_generate_webhook_signature(self):
        """Test HMAC-SHA256 signature generation"""
        payload = {"event": "query.created", "data": {"query_id": "123"}}
        secret_key = "test_secret_key"

        signature = generate_webhook_signature(payload, secret_key)

        assert signature is not None
        assert len(signature) == 64  # SHA256 hex length
        assert isinstance(signature, str)

    def test_verify_webhook_signature_valid(self):
        """Test signature verification with valid signature"""
        payload = {"event": "query.created", "data": {"query_id": "123"}}
        secret_key = "test_secret_key"

        signature = generate_webhook_signature(payload, secret_key)
        is_valid = verify_webhook_signature(payload, signature, secret_key)

        assert is_valid is True

    def test_verify_webhook_signature_invalid(self):
        """Test signature verification with invalid signature"""
        payload = {"event": "query.created", "data": {"query_id": "123"}}
        secret_key = "test_secret_key"

        invalid_signature = "invalid_signature_12345"
        is_valid = verify_webhook_signature(payload, invalid_signature, secret_key)

        assert is_valid is False

    def test_verify_webhook_signature_tampered_payload(self):
        """Test signature verification with tampered payload"""
        payload = {"event": "query.created", "data": {"query_id": "123"}}
        secret_key = "test_secret_key"

        signature = generate_webhook_signature(payload, secret_key)

        # Tamper with payload
        tampered_payload = {"event": "query.created", "data": {"query_id": "456"}}
        is_valid = verify_webhook_signature(tampered_payload, signature, secret_key)

        assert is_valid is False

    def test_signature_consistency(self):
        """Test that same payload generates same signature"""
        payload = {"event": "query.created", "data": {"query_id": "123"}}
        secret_key = "test_secret_key"

        signature1 = generate_webhook_signature(payload, secret_key)
        signature2 = generate_webhook_signature(payload, secret_key)

        assert signature1 == signature2


class TestWebhookDelivery:
    """Test webhook delivery system"""

    @pytest.mark.asyncio
    async def test_deliver_webhook_success(self):
        """Test successful webhook delivery"""
        webhook = Mock(spec=Webhook)
        webhook.id = "test-webhook-id"
        webhook.url = "https://example.com/webhook"
        webhook.secret_key = "test_secret"

        payload = {"event": "query.created", "data": {"query_id": "123"}}

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response

            result = await deliver_webhook(
                webhook, payload, max_retries=1, timeout=10
            )

            assert result["success"] is True
            assert result["status_code"] == 200
            assert result["attempts"] == 1

    @pytest.mark.asyncio
    async def test_deliver_webhook_retry_on_500(self):
        """Test webhook retry on 5xx server errors"""
        webhook = Mock(spec=Webhook)
        webhook.id = "test-webhook-id"
        webhook.url = "https://example.com/webhook"
        webhook.secret_key = "test_secret"

        payload = {"event": "query.created", "data": {"query_id": "123"}}

        with patch("httpx.AsyncClient.post") as mock_post:
            # First attempt: 500 error, second attempt: success
            mock_response_fail = AsyncMock()
            mock_response_fail.status_code = 500
            mock_response_fail.text = "Internal Server Error"

            mock_response_success = AsyncMock()
            mock_response_success.status_code = 200
            mock_response_success.text = "OK"

            mock_post.side_effect = [mock_response_fail, mock_response_success]

            result = await deliver_webhook(
                webhook, payload, max_retries=2, timeout=10
            )

            assert result["success"] is True
            assert result["attempts"] == 2
            assert mock_post.call_count == 2

    @pytest.mark.asyncio
    async def test_deliver_webhook_no_retry_on_400(self):
        """Test webhook doesn't retry on 4xx client errors"""
        webhook = Mock(spec=Webhook)
        webhook.id = "test-webhook-id"
        webhook.url = "https://example.com/webhook"
        webhook.secret_key = "test_secret"

        payload = {"event": "query.created", "data": {"query_id": "123"}}

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response

            result = await deliver_webhook(
                webhook, payload, max_retries=3, timeout=10
            )

            assert result["success"] is False
            assert result["status_code"] == 400
            assert result["attempts"] == 1  # No retry
            assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_deliver_webhook_max_retries(self):
        """Test webhook exhausts all retry attempts"""
        webhook = Mock(spec=Webhook)
        webhook.id = "test-webhook-id"
        webhook.url = "https://example.com/webhook"
        webhook.secret_key = "test_secret"

        payload = {"event": "query.created", "data": {"query_id": "123"}}

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 503
            mock_response.text = "Service Unavailable"
            mock_post.return_value = mock_response

            result = await deliver_webhook(
                webhook, payload, max_retries=3, timeout=10
            )

            assert result["success"] is False
            assert result["attempts"] == 3
            assert mock_post.call_count == 3


class TestWebhookEvents:
    """Test webhook event definitions and payload creation"""

    def test_webhook_events_constants(self):
        """Test webhook event type constants"""
        assert WebhookEvents.QUERY_CREATED == "query.created"
        assert WebhookEvents.QUERY_RESOLVED == "query.resolved"
        assert WebhookEvents.QUERY_ESCALATED == "query.escalated"
        assert WebhookEvents.FEEDBACK_RECEIVED == "feedback.received"

    def test_is_valid_event(self):
        """Test event type validation"""
        assert WebhookEvents.is_valid_event("query.created") is True
        assert WebhookEvents.is_valid_event("query.escalated") is True
        assert WebhookEvents.is_valid_event("invalid.event") is False

    def test_create_webhook_payload(self):
        """Test base webhook payload creation"""
        payload = create_webhook_payload(
            event_type="query.created",
            webhook_id="test-webhook-id",
            data={"query_id": "123", "user_id": "user_456"},
        )

        assert payload["event"] == "query.created"
        assert payload["webhook_id"] == "test-webhook-id"
        assert "timestamp" in payload
        assert payload["data"]["query_id"] == "123"

    def test_create_query_created_payload(self):
        """Test query.created event payload"""
        payload = create_query_created_payload(
            webhook_id="test-webhook-id",
            query_id="conv_123",
            user_id="user_456",
            query="How do I reset my password?",
            category="Technical",
            sentiment="Neutral",
            priority=5,
        )

        assert payload["event"] == "query.created"
        assert payload["data"]["query_id"] == "conv_123"
        assert payload["data"]["user_id"] == "user_456"
        assert payload["data"]["category"] == "Technical"
        assert payload["data"]["sentiment"] == "Neutral"
        assert payload["data"]["priority"] == 5

    def test_create_query_escalated_payload(self):
        """Test query.escalated event payload"""
        payload = create_query_escalated_payload(
            webhook_id="test-webhook-id",
            query_id="conv_123",
            user_id="user_456",
            category="Billing",
            sentiment="Angry",
            priority=9,
            escalation_reason="Billing dispute requires manual review",
            query="I was charged twice",
        )

        assert payload["event"] == "query.escalated"
        assert payload["data"]["query_id"] == "conv_123"
        assert payload["data"]["priority"] == 9
        assert payload["data"]["escalation_reason"] == "Billing dispute requires manual review"


@pytest.fixture
def db_session():
    """Create test database session"""
    from src.database.connection import SessionLocal, engine, Base

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
