"""
FastAPI routes for Multi-Agent HR Intelligence Platform
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
from sqlalchemy.orm import Session
import time

from src.api.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    KBResult,
    QueryMetadata,
)
from src.main import get_customer_support_agent
from src.utils import app_logger
from src.database.connection import get_db
from src.api.webhook_delivery import trigger_webhooks
from src.api.webhook_events import (
    create_query_created_payload,
    create_query_escalated_payload,
    WebhookEvents,
)

router = APIRouter(prefix="/api/v1", tags=["api"])

# Global agent instance
_agent = None


def get_agent():
    """Get or create agent instance"""
    global _agent
    if _agent is None:
        _agent = get_customer_support_agent()
    return _agent


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    agent=Depends(get_agent),
    db: Session = Depends(get_db),
):
    """
    Process a user query and return AI response with metadata
    """
    try:
        app_logger.info(f"Processing query from user: {request.user_id}")
        start_time = time.time()

        # Process query through agent
        result = agent.process_query(query=request.message, user_id=request.user_id)

        # Extract metadata
        metadata_dict = result.get("metadata", {})
        kb_results_raw = metadata_dict.get("kb_results", [])

        # Convert KB results to schema format
        kb_results = [
            KBResult(
                title=kb.get("title", kb.get("question", "N/A")),
                content=kb.get("content", kb.get("answer", "")),
                category=kb.get("category", "General"),
                score=kb.get("score", kb.get("similarity_score", 0.0)),
            )
            for kb in kb_results_raw
        ]

        # Build metadata response
        metadata = QueryMetadata(
            processing_time=metadata_dict.get(
                "processing_time", time.time() - start_time
            ),
            escalated=metadata_dict.get("escalated", False),
            escalation_reason=metadata_dict.get("escalation_reason"),
            kb_results=kb_results,
        )

        # Build response
        response = QueryResponse(
            conversation_id=result.get("conversation_id", "unknown"),
            response=result.get("response", "I apologize, but I encountered an error."),
            category=result.get("category", "General"),
            sentiment=result.get("sentiment", "Neutral"),
            priority=result.get("priority", 5),
            timestamp=result.get("timestamp", ""),
            metadata=metadata,
        )

        app_logger.info(
            f"Query processed successfully in {metadata.processing_time:.2f}s"
        )

        # Trigger webhooks in background (non-blocking)
        # Query created event
        query_created_payload = create_query_created_payload(
            webhook_id="",  # Will be set for each webhook
            query_id=response.conversation_id,
            user_id=request.user_id,
            query=request.message,
            category=response.category,
            sentiment=response.sentiment,
            priority=response.priority,
            metadata={
                "processing_time": metadata.processing_time,
                "kb_results_count": len(kb_results),
            },
        )

        background_tasks.add_task(
            trigger_webhooks, db, WebhookEvents.QUERY_CREATED, query_created_payload
        )

        # If escalated, trigger escalation event
        if metadata.escalated:
            query_escalated_payload = create_query_escalated_payload(
                webhook_id="",  # Will be set for each webhook
                query_id=response.conversation_id,
                user_id=request.user_id,
                category=response.category,
                sentiment=response.sentiment,
                priority=response.priority,
                escalation_reason=metadata.escalation_reason or "Unknown",
                query=request.message,
                metadata={
                    "processing_time": metadata.processing_time,
                },
            )

            background_tasks.add_task(
                trigger_webhooks,
                db,
                WebhookEvents.QUERY_ESCALATED,
                query_escalated_payload,
            )

        return response

    except Exception as e:
        app_logger.error(f"Error processing query: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    try:
        agent = get_agent()
        return HealthResponse(
            status="healthy", version="2.2.0", agent_ready=agent is not None
        )
    except Exception:
        return HealthResponse(status="unhealthy", version="2.2.0", agent_ready=False)


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """
    Get system statistics
    """
    return {
        "total_queries": 0,  # TODO: Implement from database
        "avg_response_time": 0.0,
        "active_conversations": 0,
    }
