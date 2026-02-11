"""
Database models for Multi-Agent HR Intelligence Platform
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    JSON,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class CategoryEnum(enum.Enum):
    """Query category enum - HR Domain"""

    RECRUITMENT = "Recruitment"
    PAYROLL = "Payroll"
    BENEFITS = "Benefits"
    POLICY = "Policy"
    LEAVE_MANAGEMENT = "LeaveManagement"
    PERFORMANCE = "Performance"
    GENERAL = "General"


class SentimentEnum(enum.Enum):
    """Sentiment enum"""

    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"
    ANGRY = "Angry"


class PriorityEnum(enum.Enum):
    """Priority enum"""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class StatusEnum(enum.Enum):
    """Conversation status enum"""

    ACTIVE = "Active"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"
    CLOSED = "Closed"


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    is_vip = Column(Boolean, default=False)

    # HR-specific fields
    employee_id = Column(String(50), unique=True, index=True)
    department = Column(String(100))
    position = Column(String(100))
    hire_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")


class Employee(Base):
    """Employee model - Extended HR information"""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Employee details
    department = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    employment_type = Column(String(50))  # Full-time, Part-time, Contract
    manager_id = Column(Integer, ForeignKey("employees.id"))

    # Dates
    hire_date = Column(DateTime, nullable=False)
    termination_date = Column(DateTime)

    # Compensation (stored as encrypted/hashed in production)
    salary_band = Column(String(50))  # e.g., "Band 3", "L4"

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    manager = relationship("Employee", remote_side=[id], foreign_keys=[manager_id])


class JobApplication(Base):
    """Job application tracking"""

    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)

    # Applicant information
    applicant_name = Column(String(100), nullable=False)
    applicant_email = Column(String(100), nullable=False, index=True)
    applicant_phone = Column(String(50))

    # Position details
    position_applied = Column(String(100), nullable=False, index=True)
    department = Column(String(100))
    job_posting_id = Column(String(50))

    # Application details
    resume_url = Column(String(500))
    cover_letter = Column(Text)
    status = Column(String(50), default="Submitted", index=True)
    # Status values: Submitted, Under Review, Interview Scheduled, Rejected, Offer Extended, Hired

    # Interview tracking
    interview_date = Column(DateTime)
    interviewer_notes = Column(Text)

    # Source
    application_source = Column(String(100))  # e.g., "Company Website", "LinkedIn", "Referral"
    referral_employee_id = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Conversation model"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Query details
    query = Column(Text, nullable=False)
    category = Column(String(50))
    sentiment = Column(String(50))
    priority_score = Column(Integer, default=5)

    # Response details
    response = Column(Text)
    response_time = Column(Float)  # in seconds

    # Status
    status = Column(String(50), default="Active")
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)

    # Metadata
    attempt_count = Column(Integer, default=1)
    extra_metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    feedback = relationship("Feedback", back_populates="conversation", uselist=False)


class Message(Base):
    """Individual message in a conversation"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Feedback(Base):
    """Feedback model"""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Ratings (1-5)
    rating = Column(Integer)

    # Feedback details
    comment = Column(Text)
    was_helpful = Column(Boolean)
    issues = Column(JSON)  # List of issues if any

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="feedback")
    user = relationship("User", back_populates="feedback")


class Analytics(Base):
    """Analytics aggregation model"""

    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)

    # Time period
    date = Column(DateTime, index=True, nullable=False)
    hour = Column(Integer)  # 0-23

    # Aggregated metrics
    total_queries = Column(Integer, default=0)
    recruitment_queries = Column(Integer, default=0)
    payroll_queries = Column(Integer, default=0)
    benefits_queries = Column(Integer, default=0)
    policy_queries = Column(Integer, default=0)
    leave_management_queries = Column(Integer, default=0)
    performance_queries = Column(Integer, default=0)
    general_queries = Column(Integer, default=0)

    # Sentiment counts
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    angry_count = Column(Integer, default=0)

    # Performance metrics
    avg_response_time = Column(Float)
    escalation_count = Column(Integer, default=0)
    resolution_count = Column(Integer, default=0)

    # Satisfaction
    avg_rating = Column(Float)
    feedback_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeBase(Base):
    """Knowledge base articles"""

    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)

    # Article details
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    tags = Column(JSON)  # List of tags

    # Vector embedding ID (for ChromaDB - Phase 2, commented out for Phase 1)
    # embedding_id = Column(String(100), unique=True)

    # Usage stats
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Webhook(Base):
    """Webhook endpoints for third-party integrations"""

    __tablename__ = "webhooks"

    id = Column(String(36), primary_key=True, index=True)  # UUID

    # Webhook details
    url = Column(String(500), nullable=False)
    events = Column(JSON, nullable=False)  # List of subscribed events
    secret_key = Column(String(100), nullable=False)  # For HMAC signature

    # Status
    is_active = Column(Boolean, default=True)

    # Statistics
    delivery_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_delivery_at = Column(DateTime)
    last_failure_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookDelivery(Base):
    """Log of webhook delivery attempts"""

    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(String(36), ForeignKey("webhooks.id"), index=True)

    # Delivery details
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'pending'

    # Response details
    status_code = Column(Integer)
    response_body = Column(Text)
    error_message = Column(Text)

    # Retry information
    attempt_count = Column(Integer, default=1)
    next_retry_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)

    # Relationship
    webhook = relationship("Webhook", foreign_keys=[webhook_id])
