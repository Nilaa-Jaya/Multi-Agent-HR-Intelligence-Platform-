"""
Database query operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.database.models import (
    User,
    Conversation,
    Message,
    Feedback,
    Analytics,
    KnowledgeBase,
)
from src.utils.logger import app_logger


class UserQueries:
    """User-related database queries"""

    @staticmethod
    def create_user(
        db: Session,
        user_id: str,
        name: str = None,
        email: str = None,
        is_vip: bool = False,
    ) -> User:
        """Create a new user"""
        user = User(user_id=user_id, name=name, email=email, is_vip=is_vip)
        db.add(user)
        db.commit()
        db.refresh(user)
        app_logger.info(f"Created user: {user_id}")
        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_or_create_user(db: Session, user_id: str, **kwargs) -> User:
        """Get existing user or create new one"""
        user = UserQueries.get_user(db, user_id)
        if not user:
            user = UserQueries.create_user(db, user_id, **kwargs)
        return user


class ConversationQueries:
    """Conversation-related database queries"""

    @staticmethod
    def create_conversation(
        db: Session,
        conversation_id: str,
        user_id: int,
        query: str,
        category: str = None,
        sentiment: str = None,
        priority_score: int = 5,
        extra_metadata: Dict = None,
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            query=query,
            category=category,
            sentiment=sentiment,
            priority_score=priority_score,
            extra_metadata=extra_metadata or {},
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        app_logger.info(f"Created conversation: {conversation_id}")
        return conversation

    @staticmethod
    def update_conversation(
        db: Session,
        conversation_id: str,
        response: str = None,
        response_time: float = None,
        status: str = None,
        escalated: bool = None,
        escalation_reason: str = None,
    ) -> Optional[Conversation]:
        """Update conversation details"""
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )

        if conversation:
            if response is not None:
                conversation.response = response
            if response_time is not None:
                conversation.response_time = response_time
            if status is not None:
                conversation.status = status
                if status == "Resolved":
                    conversation.resolved_at = datetime.utcnow()
            if escalated is not None:
                conversation.escalated = escalated
            if escalation_reason is not None:
                conversation.escalation_reason = escalation_reason

            db.commit()
            db.refresh(conversation)
            app_logger.info(f"Updated conversation: {conversation_id}")

        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )

    @staticmethod
    def get_user_conversations(
        db: Session, user_id: int, limit: int = 10
    ) -> List[Conversation]:
        """Get recent conversations for a user"""
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_repeat_query_count(db: Session, user_id: int, category: str) -> int:
        """Count repeat queries of same category for user"""
        return (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.category == category,
                    Conversation.created_at >= datetime.utcnow() - timedelta(days=7),
                )
            )
            .count()
        )


class MessageQueries:
    """Message-related database queries"""

    @staticmethod
    def add_message(
        db: Session, conversation_id: int, role: str, content: str
    ) -> Message:
        """Add a message to conversation"""
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation"""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )


class FeedbackQueries:
    """Feedback-related database queries"""

    @staticmethod
    def create_feedback(
        db: Session,
        conversation_id: int,
        user_id: int,
        rating: int,
        comment: str = None,
        was_helpful: bool = None,
        issues: List[str] = None,
    ) -> Feedback:
        """Create feedback for a conversation"""
        feedback = Feedback(
            conversation_id=conversation_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            was_helpful=was_helpful,
            issues=issues or [],
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        app_logger.info(f"Created feedback for conversation: {conversation_id}")
        return feedback

    @staticmethod
    def get_average_rating(db: Session, days: int = 7) -> Optional[float]:
        """Get average rating for last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        result = (
            db.query(func.avg(Feedback.rating))
            .filter(Feedback.created_at >= start_date)
            .scalar()
        )
        return float(result) if result else None


class AnalyticsQueries:
    """Analytics-related database queries"""

    @staticmethod
    def update_hourly_analytics(db: Session):
        """Update analytics for current hour"""
        now = datetime.utcnow()
        current_hour_start = now.replace(minute=0, second=0, microsecond=0)

        # Check if analytics record exists for this hour
        analytics = (
            db.query(Analytics)
            .filter(
                and_(
                    Analytics.date == current_hour_start.date(),
                    Analytics.hour == current_hour_start.hour,
                )
            )
            .first()
        )

        if not analytics:
            analytics = Analytics(
                date=current_hour_start.date(), hour=current_hour_start.hour
            )
            db.add(analytics)

        # Get conversations from this hour
        conversations = (
            db.query(Conversation)
            .filter(Conversation.created_at >= current_hour_start)
            .all()
        )

        # Calculate metrics
        analytics.total_queries = len(conversations)
        analytics.technical_queries = sum(
            1 for c in conversations if c.category == "Technical"
        )
        analytics.billing_queries = sum(
            1 for c in conversations if c.category == "Billing"
        )
        analytics.general_queries = sum(
            1 for c in conversations if c.category == "General"
        )
        analytics.account_queries = sum(
            1 for c in conversations if c.category == "Account"
        )

        analytics.positive_count = sum(
            1 for c in conversations if c.sentiment == "Positive"
        )
        analytics.neutral_count = sum(
            1 for c in conversations if c.sentiment == "Neutral"
        )
        analytics.negative_count = sum(
            1 for c in conversations if c.sentiment == "Negative"
        )
        analytics.angry_count = sum(1 for c in conversations if c.sentiment == "Angry")

        response_times = [c.response_time for c in conversations if c.response_time]
        analytics.avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        analytics.escalation_count = sum(1 for c in conversations if c.escalated)
        analytics.resolution_count = sum(
            1 for c in conversations if c.status == "Resolved"
        )

        # Get feedback for this period
        feedbacks = (
            db.query(Feedback)
            .join(Conversation)
            .filter(Conversation.created_at >= current_hour_start)
            .all()
        )

        if feedbacks:
            analytics.avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
            analytics.feedback_count = len(feedbacks)

        db.commit()
        db.refresh(analytics)
        return analytics

    @staticmethod
    def get_analytics_summary(db: Session, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)

        conversations = (
            db.query(Conversation).filter(Conversation.created_at >= start_date).all()
        )

        feedbacks = db.query(Feedback).filter(Feedback.created_at >= start_date).all()

        return {
            "total_queries": len(conversations),
            "avg_response_time": (
                sum(c.response_time for c in conversations if c.response_time)
                / len(conversations)
                if conversations
                else 0
            ),
            "escalation_rate": (
                sum(1 for c in conversations if c.escalated) / len(conversations) * 100
                if conversations
                else 0
            ),
            "resolution_rate": (
                sum(1 for c in conversations if c.status == "Resolved")
                / len(conversations)
                * 100
                if conversations
                else 0
            ),
            "avg_rating": (
                sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0
            ),
            "category_distribution": {
                "Technical": sum(1 for c in conversations if c.category == "Technical"),
                "Billing": sum(1 for c in conversations if c.category == "Billing"),
                "General": sum(1 for c in conversations if c.category == "General"),
                "Account": sum(1 for c in conversations if c.category == "Account"),
            },
            "sentiment_distribution": {
                "Positive": sum(1 for c in conversations if c.sentiment == "Positive"),
                "Neutral": sum(1 for c in conversations if c.sentiment == "Neutral"),
                "Negative": sum(1 for c in conversations if c.sentiment == "Negative"),
                "Angry": sum(1 for c in conversations if c.sentiment == "Angry"),
            },
        }


class KnowledgeBaseQueries:
    """Knowledge base queries"""

    @staticmethod
    def create_article(
        db: Session,
        title: str,
        content: str,
        category: str = None,
        tags: List[str] = None,
        embedding_id: str = None,
    ) -> KnowledgeBase:
        """Create knowledge base article"""
        article = KnowledgeBase(
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            embedding_id=embedding_id,
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        app_logger.info(f"Created KB article: {title}")
        return article

    @staticmethod
    def get_articles_by_category(db: Session, category: str) -> List[KnowledgeBase]:
        """Get articles by category"""
        return (
            db.query(KnowledgeBase)
            .filter(
                and_(
                    KnowledgeBase.category == category,
                    KnowledgeBase.is_active.is_(True),
                )
            )
            .all()
        )

    @staticmethod
    def increment_view_count(db: Session, article_id: int):
        """Increment article view count"""
        article = db.query(KnowledgeBase).filter(KnowledgeBase.id == article_id).first()
        if article:
            article.view_count += 1
            db.commit()
