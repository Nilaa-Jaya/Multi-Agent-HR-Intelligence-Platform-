"""
Webhook delivery system with retry logic and HMAC signatures
"""

import asyncio
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

import httpx

from src.database.models import Webhook
from src.database.webhook_queries import WebhookQueries
from src.utils.logger import app_logger


def generate_webhook_signature(payload: Dict[str, Any], secret_key: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payload

    Args:
        payload: Webhook payload dict
        secret_key: Webhook secret key

    Returns:
        HMAC signature as hex string
    """
    # Convert payload to JSON string
    payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        key=secret_key.encode("utf-8"),
        msg=payload_str.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return signature


async def deliver_webhook(
    webhook: Webhook,
    payload: Dict[str, Any],
    max_retries: int = 3,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Deliver webhook with retry logic

    Args:
        webhook: Webhook instance
        payload: Event payload
        max_retries: Maximum number of delivery attempts
        timeout: Timeout for each attempt in seconds

    Returns:
        Dict with delivery status:
        {
            "success": bool,
            "status_code": int,
            "response_body": str,
            "error": str,
            "attempts": int,
            "response_time_ms": float
        }
    """
    # Generate signature
    signature = generate_webhook_signature(payload, webhook.secret_key)
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Timestamp": timestamp,
        "X-Webhook-ID": webhook.id,
        "User-Agent": "Multi-Agent HR Intelligence Platform-Webhook/1.0",
    }

    # Retry logic with exponential backoff
    for attempt in range(1, max_retries + 1):
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    webhook.url, json=payload, headers=headers
                )

                response_time_ms = (time.time() - start_time) * 1000

                # Check if successful (2xx status codes)
                if 200 <= response.status_code < 300:
                    app_logger.info(
                        f"Webhook {webhook.id} delivered successfully on attempt {attempt}"
                    )

                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "response_body": response.text[:1000],  # Limit to 1000 chars
                        "error": None,
                        "attempts": attempt,
                        "response_time_ms": response_time_ms,
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    app_logger.warning(
                        f"Webhook {webhook.id} failed on attempt {attempt}: {error_msg}"
                    )

                    # Don't retry for client errors (4xx)
                    if 400 <= response.status_code < 500:
                        return {
                            "success": False,
                            "status_code": response.status_code,
                            "response_body": response.text[:1000],
                            "error": error_msg,
                            "attempts": attempt,
                            "response_time_ms": response_time_ms,
                        }

                    # Retry for server errors (5xx)
                    if attempt < max_retries:
                        # Exponential backoff: 1s, 2s, 4s
                        backoff_seconds = 2 ** (attempt - 1)
                        app_logger.info(
                            f"Retrying webhook {webhook.id} in {backoff_seconds}s..."
                        )
                        await asyncio.sleep(backoff_seconds)
                        continue
                    else:
                        return {
                            "success": False,
                            "status_code": response.status_code,
                            "response_body": response.text[:1000],
                            "error": error_msg,
                            "attempts": attempt,
                            "response_time_ms": response_time_ms,
                        }

        except httpx.TimeoutException as e:
            error_msg = f"Timeout after {timeout}s: {str(e)}"
            app_logger.warning(
                f"Webhook {webhook.id} timeout on attempt {attempt}: {error_msg}"
            )

            if attempt < max_retries:
                backoff_seconds = 2 ** (attempt - 1)
                await asyncio.sleep(backoff_seconds)
                continue
            else:
                return {
                    "success": False,
                    "status_code": None,
                    "response_body": None,
                    "error": error_msg,
                    "attempts": attempt,
                    "response_time_ms": (time.time() - start_time) * 1000,
                }

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            app_logger.error(
                f"Webhook {webhook.id} error on attempt {attempt}: {error_msg}"
            )

            if attempt < max_retries:
                backoff_seconds = 2 ** (attempt - 1)
                await asyncio.sleep(backoff_seconds)
                continue
            else:
                return {
                    "success": False,
                    "status_code": None,
                    "response_body": None,
                    "error": error_msg,
                    "attempts": attempt,
                    "response_time_ms": (time.time() - start_time) * 1000,
                }

    # Should never reach here, but just in case
    return {
        "success": False,
        "status_code": None,
        "response_body": None,
        "error": "Max retries exceeded",
        "attempts": max_retries,
        "response_time_ms": 0,
    }


async def trigger_webhooks(
    db_session,
    event_type: str,
    payload: Dict[str, Any],
    log_delivery: bool = True,
) -> None:
    """
    Trigger all webhooks subscribed to an event (non-blocking)

    Args:
        db_session: Database session
        event_type: Event type (e.g., 'query.created')
        payload: Event payload
        log_delivery: Whether to log delivery attempts
    """
    # Get active webhooks for this event
    webhooks = WebhookQueries.get_active_webhooks_for_event(db_session, event_type)

    if not webhooks:
        app_logger.debug(f"No active webhooks for event: {event_type}")
        return

    app_logger.info(
        f"Triggering {len(webhooks)} webhook(s) for event: {event_type}"
    )

    # Deliver to each webhook (in parallel, non-blocking)
    delivery_tasks = []

    for webhook in webhooks:
        # Create payload for this specific webhook
        webhook_payload = payload.copy()
        webhook_payload["webhook_id"] = webhook.id

        # Create delivery task
        task = deliver_webhook_and_log(
            db_session, webhook, webhook_payload, event_type, log_delivery
        )
        delivery_tasks.append(task)

    # Fire and forget (don't wait for completion)
    # This ensures webhook delivery doesn't block the main request
    if delivery_tasks:
        asyncio.create_task(asyncio.gather(*delivery_tasks, return_exceptions=True))


async def deliver_webhook_and_log(
    db_session,
    webhook: Webhook,
    payload: Dict[str, Any],
    event_type: str,
    log_delivery: bool,
) -> None:
    """
    Deliver webhook and log the result

    Args:
        db_session: Database session
        webhook: Webhook instance
        payload: Event payload
        event_type: Event type
        log_delivery: Whether to log delivery
    """
    try:
        # Deliver webhook
        result = await deliver_webhook(webhook, payload)

        # Update webhook statistics
        WebhookQueries.update_delivery_stats(
            db_session, webhook.id, result["success"]
        )

        # Log delivery if requested
        if log_delivery:
            status = "success" if result["success"] else "failed"
            WebhookQueries.create_delivery_log(
                db=db_session,
                webhook_id=webhook.id,
                event_type=event_type,
                payload=payload,
                status=status,
                status_code=result.get("status_code"),
                response_body=result.get("response_body"),
                error_message=result.get("error"),
                attempt_count=result.get("attempts", 1),
            )

        if result["success"]:
            app_logger.info(
                f"Webhook {webhook.id} delivered successfully to {webhook.url}"
            )
        else:
            app_logger.error(
                f"Webhook {webhook.id} delivery failed: {result.get('error')}"
            )

    except Exception as e:
        app_logger.error(f"Error delivering webhook {webhook.id}: {str(e)}")
        # Update failure stats
        WebhookQueries.update_delivery_stats(db_session, webhook.id, False)


def verify_webhook_signature(
    payload: Dict[str, Any], signature: str, secret_key: str
) -> bool:
    """
    Verify webhook signature (for webhook receivers)

    Args:
        payload: Webhook payload
        signature: Signature from X-Webhook-Signature header
        secret_key: Webhook secret key

    Returns:
        True if signature is valid
    """
    expected_signature = generate_webhook_signature(payload, secret_key)
    return hmac.compare_digest(signature, expected_signature)
