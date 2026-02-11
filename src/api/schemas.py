"""
Pydantic schemas for FastAPI request/response models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for chat query"""

    message: str = Field(..., min_length=1, description="User message")
    user_id: str = Field(default="web_user", description="User identifier")
    conversation_id: Optional[str] = Field(
        None, description="Conversation ID for context"
    )


class KBResult(BaseModel):
    """Knowledge base result"""

    title: str
    content: str
    category: str
    score: float


class QueryMetadata(BaseModel):
    """Query analysis metadata"""

    processing_time: float
    escalated: bool
    escalation_reason: Optional[str] = None
    kb_results: List[KBResult] = []


class QueryResponse(BaseModel):
    """Response model for chat query"""

    conversation_id: str
    response: str
    category: str
    sentiment: str
    priority: int
    timestamp: str
    metadata: QueryMetadata


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    agent_ready: bool


class ExportConversation(BaseModel):
    """Export conversation data"""

    conversation_id: str
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]


# Webhook Schemas


class WebhookCreate(BaseModel):
    """Create new webhook"""

    url: str
    events: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhooks/smartsupport",
                "events": ["query.created", "query.escalated"],
            }
        }


class WebhookUpdate(BaseModel):
    """Update existing webhook"""

    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhooks/new-endpoint",
                "is_active": True,
            }
        }


class WebhookResponse(BaseModel):
    """Webhook response"""

    id: str
    url: str
    events: List[str]
    secret_key: str
    is_active: bool
    delivery_count: int
    failure_count: int
    last_delivery_at: Optional[str] = None
    last_failure_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    """List of webhooks"""

    webhooks: List[WebhookResponse]
    total: int
    skip: int
    limit: int


class WebhookTestResponse(BaseModel):
    """Webhook test delivery response"""

    success: bool
    status_code: Optional[int] = None
    response_time_ms: float
    error: Optional[str] = None


class WebhookDeliveryLogResponse(BaseModel):
    """Webhook delivery log entry"""

    id: int
    webhook_id: str
    event_type: str
    payload: Dict[str, Any]
    status: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int
    created_at: str
    delivered_at: Optional[str] = None

    class Config:
        from_attributes = True


class WebhookDeliveryLogsResponse(BaseModel):
    """List of webhook delivery logs"""

    logs: List[WebhookDeliveryLogResponse]
    total: int
    skip: int
    limit: int
