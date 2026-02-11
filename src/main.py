"""
Multi-Agent HR Intelligence Platform - Main Orchestrator
Version: 3.0.0
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.workflow import get_workflow
from src.agents.state import ConversationContext
from src.database import (
    get_db_context,
    UserQueries,
    ConversationQueries,
    MessageQueries,
)
from src.utils import app_logger, generate_conversation_id, format_response, Timer


class CustomerSupportAgent:
    """
    Main customer support agent orchestrator

    Coordinates the entire workflow from query to response
    """

    def __init__(self):
        """Initialize the customer support agent"""
        self.workflow = get_workflow()
        app_logger.info("CustomerSupportAgent initialized")

    def process_query(
        self,
        query: str,
        user_id: str = "anonymous",
        conversation_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a customer support query

        Args:
            query: Customer query text
            user_id: User identifier
            conversation_id: Optional existing conversation ID
            user_context: Optional user context (VIP status, history, etc.)

        Returns:
            Response dictionary with all relevant information
        """
        app_logger.info(f"Processing query from user {user_id}: {query[:100]}...")

        # Start timer
        timer = Timer("Query Processing")
        timer.__enter__()

        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = generate_conversation_id()

            # Get or create user in database
            with get_db_context() as db:
                user = UserQueries.get_or_create_user(db, user_id)
                user_db_id = user.id

                # Get conversation history
                recent_convs = ConversationQueries.get_user_conversations(
                    db, user.id, limit=5
                )
                conversation_history = []
                for conv in recent_convs:
                    messages = MessageQueries.get_conversation_messages(db, conv.id)
                    for msg in messages[-3:]:  # Last 3 messages from each conversation
                        conversation_history.append(
                            {"role": msg.role, "content": msg.content}
                        )

                # Prepare user context
                # NOTE: attempt_count should only increment for the SAME query repeated
                # Currently we don't have same-query detection, so default to 1
                if not user_context:
                    user_context = {}
                user_context["is_vip"] = user.is_vip
                user_context["is_repeat_query"] = (
                    False  # TODO: Implement proper same-query detection
                )
                user_context["attempt_count"] = 1  # Always 1 unless same query detected

            # Create conversation context
            context = ConversationContext(
                query=query,
                user_id=user_id,
                conversation_id=conversation_id,
                user_context=user_context,
                conversation_history=conversation_history,
            )

            # Convert to agent state
            state = context.to_state()
            state["user_db_id"] = user_db_id

            # Run workflow
            app_logger.info(f"Running workflow for conversation {conversation_id}")
            result = self.workflow.invoke(state)

            # Debug logging for kb_results
            app_logger.info(f"[MAIN DEBUG] Result keys: {list(result.keys())}")
            kb_results_from_workflow = result.get("kb_results", [])
            app_logger.info(
                f"[MAIN DEBUG] KB results from workflow: {len(kb_results_from_workflow)} items"
            )
            if kb_results_from_workflow:
                app_logger.info(
                    f"[MAIN DEBUG] First KB result: {kb_results_from_workflow[0]}"
                )

            # Stop timer
            timer.__exit__()
            processing_time = timer.elapsed

            # Save to database
            with get_db_context() as db:
                # Create conversation record
                conversation = ConversationQueries.create_conversation(
                    db=db,
                    conversation_id=conversation_id,
                    user_id=user_db_id,
                    query=query,
                    category=result.get("category"),
                    sentiment=result.get("sentiment"),
                    priority_score=result.get("priority_score", 5),
                    extra_metadata=result.get("extra_metadata", {}),
                )

                # Update with response
                ConversationQueries.update_conversation(
                    db=db,
                    conversation_id=conversation_id,
                    response=result.get("response"),
                    response_time=processing_time,
                    status="Escalated" if result.get("should_escalate") else "Resolved",
                    escalated=result.get("should_escalate", False),
                    escalation_reason=result.get("escalation_reason"),
                )

                # Add messages
                MessageQueries.add_message(db, conversation.id, "user", query)
                MessageQueries.add_message(
                    db, conversation.id, "assistant", result.get("response", "")
                )

            # Format response
            kb_results_for_metadata = result.get("kb_results", [])
            app_logger.info(
                f"[MAIN DEBUG] Passing {len(kb_results_for_metadata)} KB results to metadata"
            )

            response = format_response(
                response=result.get("response", ""),
                category=result.get("category", "General"),
                sentiment=result.get("sentiment", "Neutral"),
                priority=result.get("priority_score", 5),
                conversation_id=conversation_id,
                metadata={
                    "processing_time": processing_time,
                    "escalated": result.get("should_escalate", False),
                    "escalation_reason": result.get("escalation_reason"),
                    "kb_results": kb_results_for_metadata,
                    **result.get("extra_metadata", {}),
                },
            )

            app_logger.info(
                f"[MAIN DEBUG] Response metadata contains kb_results: {'kb_results' in response.get('metadata', {})}"
            )

            app_logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return response

        except Exception as e:
            app_logger.error(f"Error processing query: {e}", exc_info=True)

            # Return error response
            return {
                "conversation_id": conversation_id or "error",
                "response": "I apologize, but I encountered an error processing your request. Please try again or contact support.",
                "category": "Error",
                "sentiment": "Neutral",
                "priority": 5,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": str(e), "success": False},
            }

    def get_conversation_history(self, user_id: str, limit: int = 10) -> list:
        """
        Get conversation history for a user

        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return

        Returns:
            List of conversation dictionaries
        """
        with get_db_context() as db:
            user = UserQueries.get_user(db, user_id)
            if not user:
                return []

            conversations = ConversationQueries.get_user_conversations(
                db, user.id, limit
            )

            history = []
            for conv in conversations:
                history.append(
                    {
                        "conversation_id": conv.conversation_id,
                        "query": conv.query,
                        "response": conv.response,
                        "category": conv.category,
                        "sentiment": conv.sentiment,
                        "timestamp": conv.created_at.isoformat(),
                        "escalated": conv.escalated,
                    }
                )

            return history


# Global agent instance
_agent: Optional[CustomerSupportAgent] = None


def get_customer_support_agent() -> CustomerSupportAgent:
    """Get or create customer support agent singleton"""
    global _agent
    if _agent is None:
        _agent = CustomerSupportAgent()
    return _agent
