"""
Webhook event definitions and payload generators
"""

from datetime import datetime
from typing import Dict, Any


# Event type constants
class WebhookEvents:
    """Webhook event type constants"""

    QUERY_CREATED = "query.created"
    QUERY_RESOLVED = "query.resolved"
    QUERY_ESCALATED = "query.escalated"
    FEEDBACK_RECEIVED = "feedback.received"

    @classmethod
    def all_events(cls) -> list:
        """Get all available event types"""
        return [
            cls.QUERY_CREATED,
            cls.QUERY_RESOLVED,
            cls.QUERY_ESCALATED,
            cls.FEEDBACK_RECEIVED,
        ]

    @classmethod
    def is_valid_event(cls, event: str) -> bool:
        """Check if event type is valid"""
        return event in cls.all_events()


def create_webhook_payload(
    event_type: str,
    webhook_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create webhook payload with standard format

    Args:
        event_type: Type of event
        webhook_id: Webhook ID receiving the event
        data: Event-specific data

    Returns:
        Formatted webhook payload
    """
    return {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "webhook_id": webhook_id,
        "data": data,
    }


def create_query_created_payload(
    webhook_id: str,
    query_id: str,
    user_id: str,
    query: str,
    category: str,
    sentiment: str,
    priority: int,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Create payload for query.created event

    Args:
        webhook_id: Webhook ID
        query_id: Conversation/query ID
        user_id: User ID
        query: User query text
        category: Query category
        sentiment: Detected sentiment
        priority: Priority score
        metadata: Additional metadata

    Returns:
        Webhook payload
    """
    data = {
        "query_id": query_id,
        "user_id": user_id,
        "category": category,
        "sentiment": sentiment,
        "priority": priority,
        "query": query,
    }

    if metadata:
        data["metadata"] = metadata

    return create_webhook_payload(WebhookEvents.QUERY_CREATED, webhook_id, data)


def create_query_resolved_payload(
    webhook_id: str,
    query_id: str,
    user_id: str,
    category: str,
    resolution_time_seconds: float,
    response: str,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Create payload for query.resolved event

    Args:
        webhook_id: Webhook ID
        query_id: Conversation/query ID
        user_id: User ID
        category: Query category
        resolution_time_seconds: Time to resolve in seconds
        response: Final response
        metadata: Additional metadata

    Returns:
        Webhook payload
    """
    data = {
        "query_id": query_id,
        "user_id": user_id,
        "category": category,
        "resolution_time_seconds": resolution_time_seconds,
        "response": response,
    }

    if metadata:
        data["metadata"] = metadata

    return create_webhook_payload(WebhookEvents.QUERY_RESOLVED, webhook_id, data)


def create_query_escalated_payload(
    webhook_id: str,
    query_id: str,
    user_id: str,
    category: str,
    sentiment: str,
    priority: int,
    escalation_reason: str,
    query: str,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Create payload for query.escalated event

    Args:
        webhook_id: Webhook ID
        query_id: Conversation/query ID
        user_id: User ID
        category: Query category
        sentiment: Detected sentiment
        priority: Priority score
        escalation_reason: Reason for escalation
        query: User query text
        metadata: Additional metadata

    Returns:
        Webhook payload
    """
    data = {
        "query_id": query_id,
        "user_id": user_id,
        "category": category,
        "sentiment": sentiment,
        "priority": priority,
        "escalation_reason": escalation_reason,
        "query": query,
    }

    if metadata:
        data["metadata"] = metadata

    return create_webhook_payload(WebhookEvents.QUERY_ESCALATED, webhook_id, data)


def create_feedback_received_payload(
    webhook_id: str,
    query_id: str,
    user_id: str,
    rating: int,
    feedback_text: str = None,
    category: str = None,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Create payload for feedback.received event

    Args:
        webhook_id: Webhook ID
        query_id: Conversation/query ID
        user_id: User ID
        rating: Feedback rating (1-5)
        feedback_text: Optional feedback text
        category: Query category
        metadata: Additional metadata

    Returns:
        Webhook payload
    """
    data = {
        "query_id": query_id,
        "user_id": user_id,
        "rating": rating,
    }

    if feedback_text:
        data["feedback_text"] = feedback_text
    if category:
        data["category"] = category
    if metadata:
        data["metadata"] = metadata

    return create_webhook_payload(WebhookEvents.FEEDBACK_RECEIVED, webhook_id, data)
