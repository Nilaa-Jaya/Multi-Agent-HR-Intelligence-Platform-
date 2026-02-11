"""
Webhook management API endpoints
"""

import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.webhook_queries import WebhookQueries
from src.api.schemas import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
    WebhookTestResponse,
    WebhookDeliveryLogsResponse,
    WebhookDeliveryLogResponse,
)
from src.api.webhook_delivery import deliver_webhook
from src.api.webhook_events import WebhookEvents, create_webhook_payload
from src.utils.logger import app_logger

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate, db: Session = Depends(get_db)
):
    """
    Register a new webhook

    - **url**: Webhook endpoint URL (must be HTTPS in production)
    - **events**: List of event types to subscribe to

    Returns the webhook with generated secret_key for signature verification.
    """
    # Validate URL format
    if not webhook_data.url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://",
        )

    # Validate events
    for event in webhook_data.events:
        if not WebhookEvents.is_valid_event(event):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {event}. Valid events: {WebhookEvents.all_events()}",
            )

    # Create webhook
    webhook = WebhookQueries.create_webhook(
        db=db, url=webhook_data.url, events=webhook_data.events
    )

    app_logger.info(f"Created webhook {webhook.id} for URL: {webhook.url}")

    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events,
        secret_key=webhook.secret_key,
        is_active=webhook.is_active,
        delivery_count=webhook.delivery_count,
        failure_count=webhook.failure_count,
        last_delivery_at=(
            webhook.last_delivery_at.isoformat() if webhook.last_delivery_at else None
        ),
        last_failure_at=(
            webhook.last_failure_at.isoformat() if webhook.last_failure_at else None
        ),
        created_at=webhook.created_at.isoformat(),
        updated_at=webhook.updated_at.isoformat(),
    )


@router.get("/", response_model=WebhookListResponse)
async def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
):
    """
    List all webhooks with pagination

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status (optional)
    """
    webhooks = WebhookQueries.list_webhooks(
        db=db, skip=skip, limit=limit, is_active=is_active
    )

    webhook_responses = [
        WebhookResponse(
            id=w.id,
            url=w.url,
            events=w.events,
            secret_key=w.secret_key,
            is_active=w.is_active,
            delivery_count=w.delivery_count,
            failure_count=w.failure_count,
            last_delivery_at=w.last_delivery_at.isoformat() if w.last_delivery_at else None,
            last_failure_at=w.last_failure_at.isoformat() if w.last_failure_at else None,
            created_at=w.created_at.isoformat(),
            updated_at=w.updated_at.isoformat(),
        )
        for w in webhooks
    ]

    return WebhookListResponse(
        webhooks=webhook_responses,
        total=len(webhook_responses),
        skip=skip,
        limit=limit,
    )


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """
    Get a specific webhook by ID
    """
    webhook = WebhookQueries.get_webhook(db=db, webhook_id=webhook_id)

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found"
        )

    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events,
        secret_key=webhook.secret_key,
        is_active=webhook.is_active,
        delivery_count=webhook.delivery_count,
        failure_count=webhook.failure_count,
        last_delivery_at=(
            webhook.last_delivery_at.isoformat() if webhook.last_delivery_at else None
        ),
        last_failure_at=(
            webhook.last_failure_at.isoformat() if webhook.last_failure_at else None
        ),
        created_at=webhook.created_at.isoformat(),
        updated_at=webhook.updated_at.isoformat(),
    )


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str, webhook_data: WebhookUpdate, db: Session = Depends(get_db)
):
    """
    Update a webhook

    - **url**: New webhook URL (optional)
    - **events**: New list of event types (optional)
    - **is_active**: Enable/disable webhook (optional)
    """
    # Validate URL if provided
    if webhook_data.url and not webhook_data.url.startswith(
        ("http://", "https://")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://",
        )

    # Validate events if provided
    if webhook_data.events:
        for event in webhook_data.events:
            if not WebhookEvents.is_valid_event(event):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid event type: {event}",
                )

    webhook = WebhookQueries.update_webhook(
        db=db,
        webhook_id=webhook_id,
        url=webhook_data.url,
        events=webhook_data.events,
        is_active=webhook_data.is_active,
    )

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found"
        )

    app_logger.info(f"Updated webhook {webhook_id}")

    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events,
        secret_key=webhook.secret_key,
        is_active=webhook.is_active,
        delivery_count=webhook.delivery_count,
        failure_count=webhook.failure_count,
        last_delivery_at=(
            webhook.last_delivery_at.isoformat() if webhook.last_delivery_at else None
        ),
        last_failure_at=(
            webhook.last_failure_at.isoformat() if webhook.last_failure_at else None
        ),
        created_at=webhook.created_at.isoformat(),
        updated_at=webhook.updated_at.isoformat(),
    )


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """
    Delete a webhook
    """
    deleted = WebhookQueries.delete_webhook(db=db, webhook_id=webhook_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found"
        )

    app_logger.info(f"Deleted webhook {webhook_id}")
    return None


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """
    Test webhook delivery with a sample payload

    Sends a test event to verify webhook endpoint is working
    """
    webhook = WebhookQueries.get_webhook(db=db, webhook_id=webhook_id)

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found"
        )

    # Create test payload
    test_payload = create_webhook_payload(
        event_type="webhook.test",
        webhook_id=webhook.id,
        data={
            "message": "This is a test webhook delivery",
            "test": True,
        },
    )

    # Deliver webhook
    start_time = time.time()
    result = await deliver_webhook(webhook, test_payload, max_retries=1, timeout=10)
    response_time_ms = (time.time() - start_time) * 1000

    app_logger.info(f"Test webhook {webhook_id} delivery result: {result}")

    return WebhookTestResponse(
        success=result["success"],
        status_code=result.get("status_code"),
        response_time_ms=response_time_ms,
        error=result.get("error"),
    )


@router.get("/{webhook_id}/deliveries", response_model=WebhookDeliveryLogsResponse)
async def get_webhook_deliveries(
    webhook_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get delivery logs for a webhook

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    webhook = WebhookQueries.get_webhook(db=db, webhook_id=webhook_id)

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found"
        )

    logs = WebhookQueries.get_delivery_logs(
        db=db, webhook_id=webhook_id, skip=skip, limit=limit
    )

    log_responses = [
        WebhookDeliveryLogResponse(
            id=log.id,
            webhook_id=log.webhook_id,
            event_type=log.event_type,
            payload=log.payload,
            status=log.status,
            status_code=log.status_code,
            response_body=log.response_body,
            error_message=log.error_message,
            attempt_count=log.attempt_count,
            created_at=log.created_at.isoformat(),
            delivered_at=log.delivered_at.isoformat() if log.delivered_at else None,
        )
        for log in logs
    ]

    return WebhookDeliveryLogsResponse(
        logs=log_responses,
        total=len(log_responses),
        skip=skip,
        limit=limit,
    )
