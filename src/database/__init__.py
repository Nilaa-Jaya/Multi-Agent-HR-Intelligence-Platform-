"""
Database package for Multi-Agent HR Intelligence Platform
"""

from src.database.models import (
    Base,
    User,
    Conversation,
    Message,
    Feedback,
    Analytics,
    KnowledgeBase,
    Webhook,
    WebhookDelivery,
)
from src.database.connection import (
    engine,
    SessionLocal,
    init_db,
    get_db,
    get_db_context,
    close_db,
)
from src.database.queries import (
    UserQueries,
    ConversationQueries,
    MessageQueries,
    FeedbackQueries,
    AnalyticsQueries,
    KnowledgeBaseQueries,
)
from src.database.webhook_queries import WebhookQueries

__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "Feedback",
    "Analytics",
    "KnowledgeBase",
    "Webhook",
    "WebhookDelivery",
    "engine",
    "SessionLocal",
    "init_db",
    "get_db",
    "get_db_context",
    "close_db",
    "UserQueries",
    "ConversationQueries",
    "MessageQueries",
    "FeedbackQueries",
    "AnalyticsQueries",
    "KnowledgeBaseQueries",
    "WebhookQueries",
]
