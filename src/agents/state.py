"""
State management for Multi-Agent HR Intelligence Platform agent workflow
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class AgentState(TypedDict):
    """
    State structure for the customer support agent workflow

    This state is passed between all nodes in the LangGraph workflow
    """

    # Input
    query: str
    user_id: str
    conversation_id: str

    # Analysis results
    category: Optional[str]
    sentiment: Optional[str]
    priority_score: Optional[int]

    # Context
    user_context: Optional[Dict[str, Any]]  # User history, VIP status, etc.
    conversation_history: Optional[List[Dict[str, str]]]  # Previous messages

    # Knowledge base
    kb_results: Optional[List[Dict[str, Any]]]  # Retrieved KB articles

    # Response
    response: Optional[str]

    # Routing decisions
    should_escalate: bool
    escalation_reason: Optional[str]
    next_action: Optional[str]

    # Metadata
    metadata: Optional[Dict[str, Any]]
    processing_time: Optional[float]

    # Database IDs
    user_db_id: Optional[int]
    conversation_db_id: Optional[int]


class ConversationContext:
    """Helper class to manage conversation context"""

    def __init__(
        self,
        query: str,
        user_id: str,
        conversation_id: str,
        user_context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None,
    ):
        self.query = query
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.user_context = user_context or {}
        self.conversation_history = conversation_history or []
        self.start_time = datetime.now()

    def to_state(self) -> AgentState:
        """Convert to AgentState"""
        return AgentState(
            query=self.query,
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            user_context=self.user_context,
            conversation_history=self.conversation_history,
            category=None,
            sentiment=None,
            priority_score=None,
            kb_results=None,
            response=None,
            should_escalate=False,
            escalation_reason=None,
            next_action=None,
            metadata={},
            processing_time=None,
            user_db_id=None,
            conversation_db_id=None,
        )

    def get_processing_time(self) -> float:
        """Get elapsed processing time"""
        return (datetime.now() - self.start_time).total_seconds()

    def format_history_for_llm(self) -> str:
        """Format conversation history for LLM context"""
        if not self.conversation_history:
            return ""

        formatted = ["Previous conversation:"]
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")

        return "\n".join(formatted)
