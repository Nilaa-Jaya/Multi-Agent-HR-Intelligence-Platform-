"""
Database queries for webhook operations
"""

import uuid
import secrets
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from src.database.models import Webhook, WebhookDelivery
from src.utils.logger import app_logger


class WebhookQueries:
    """Database operations for webhooks"""

    @staticmethod
    def create_webhook(
        db: Session, url: str, events: List[str], secret_key: Optional[str] = None
    ) -> Webhook:
        """
        Create a new webhook

        Args:
            db: Database session
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            secret_key: Optional custom secret key (auto-generated if not provided)

        Returns:
            Created webhook instance
        """
        webhook_id = str(uuid.uuid4())

        # Generate secret key if not provided
        if not secret_key:
            secret_key = secrets.token_urlsafe(32)

        webhook = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            secret_key=secret_key,
            is_active=True,
        )

        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        app_logger.info(f"Created webhook {webhook_id} for URL: {url}")
        return webhook

    @staticmethod
    def get_webhook(db: Session, webhook_id: str) -> Optional[Webhook]:
        """
        Get webhook by ID

        Args:
            db: Database session
            webhook_id: Webhook UUID

        Returns:
            Webhook instance or None
        """
        return db.query(Webhook).filter(Webhook.id == webhook_id).first()

    @staticmethod
    def list_webhooks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Webhook]:
        """
        List webhooks with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (None = all)

        Returns:
            List of webhooks
        """
        query = db.query(Webhook)

        if is_active is not None:
            query = query.filter(Webhook.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_webhook(
        db: Session,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Webhook]:
        """
        Update webhook

        Args:
            db: Database session
            webhook_id: Webhook UUID
            url: New URL (optional)
            events: New events list (optional)
            is_active: New active status (optional)

        Returns:
            Updated webhook or None if not found
        """
        webhook = WebhookQueries.get_webhook(db, webhook_id)
        if not webhook:
            return None

        if url is not None:
            webhook.url = url
        if events is not None:
            webhook.events = events
        if is_active is not None:
            webhook.is_active = is_active

        webhook.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(webhook)

        app_logger.info(f"Updated webhook {webhook_id}")
        return webhook

    @staticmethod
    def delete_webhook(db: Session, webhook_id: str) -> bool:
        """
        Delete webhook

        Args:
            db: Database session
            webhook_id: Webhook UUID

        Returns:
            True if deleted, False if not found
        """
        webhook = WebhookQueries.get_webhook(db, webhook_id)
        if not webhook:
            return False

        db.delete(webhook)
        db.commit()

        app_logger.info(f"Deleted webhook {webhook_id}")
        return True

    @staticmethod
    def get_active_webhooks_for_event(
        db: Session, event_type: str
    ) -> List[Webhook]:
        """
        Get all active webhooks subscribed to a specific event

        Args:
            db: Database session
            event_type: Event type (e.g., 'query.created')

        Returns:
            List of active webhooks subscribed to the event
        """
        webhooks = (
            db.query(Webhook)
            .filter(Webhook.is_active.is_(True))
            .all()
        )

        # Filter webhooks that have this event in their events list
        matching_webhooks = [
            webhook for webhook in webhooks if event_type in webhook.events
        ]

        return matching_webhooks

    @staticmethod
    def update_delivery_stats(
        db: Session, webhook_id: str, success: bool
    ) -> None:
        """
        Update webhook delivery statistics

        Args:
            db: Database session
            webhook_id: Webhook UUID
            success: Whether delivery was successful
        """
        webhook = WebhookQueries.get_webhook(db, webhook_id)
        if not webhook:
            return

        webhook.delivery_count += 1

        if success:
            webhook.last_delivery_at = datetime.utcnow()
        else:
            webhook.failure_count += 1
            webhook.last_failure_at = datetime.utcnow()

        db.commit()

    @staticmethod
    def create_delivery_log(
        db: Session,
        webhook_id: str,
        event_type: str,
        payload: dict,
        status: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        error_message: Optional[str] = None,
        attempt_count: int = 1,
    ) -> WebhookDelivery:
        """
        Create a webhook delivery log entry

        Args:
            db: Database session
            webhook_id: Webhook UUID
            event_type: Type of event delivered
            payload: Event payload
            status: Delivery status ('success', 'failed', 'pending')
            status_code: HTTP status code
            response_body: Response from webhook endpoint
            error_message: Error message if failed
            attempt_count: Number of delivery attempts

        Returns:
            Created delivery log
        """
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event_type=event_type,
            payload=payload,
            status=status,
            status_code=status_code,
            response_body=response_body,
            error_message=error_message,
            attempt_count=attempt_count,
        )

        if status == "success":
            delivery.delivered_at = datetime.utcnow()

        db.add(delivery)
        db.commit()
        db.refresh(delivery)

        return delivery

    @staticmethod
    def get_delivery_logs(
        db: Session,
        webhook_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[WebhookDelivery]:
        """
        Get delivery logs for a webhook

        Args:
            db: Database session
            webhook_id: Webhook UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of delivery logs
        """
        return (
            db.query(WebhookDelivery)
            .filter(WebhookDelivery.webhook_id == webhook_id)
            .order_by(WebhookDelivery.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
