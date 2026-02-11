"""
Escalation agent
"""

from src.agents.state import AgentState
from src.utils.helpers import should_escalate
from src.utils.logger import app_logger


def check_escalation(state: AgentState) -> AgentState:
    """
    Check if query should be escalated to human agent

    Args:
        state: Current agent state

    Returns:
        Updated state with escalation decision
    """
    app_logger.info("Checking escalation criteria...")

    # Determine escalation using updated should_escalate function
    needs_escalation, escalation_reason = should_escalate(
        priority_score=state.get("priority_score", 5),
        sentiment=state.get("sentiment", "Neutral"),
        attempt_count=state.get("user_context", {}).get("attempt_count", 1),
        query=state["query"],
    )

    if needs_escalation:
        app_logger.warning(f"Query flagged for escalation: {state['query'][:50]}...")
        app_logger.warning(f"Escalation reason: {escalation_reason}")
        state["should_escalate"] = True
        state["escalation_reason"] = escalation_reason or "Manual escalation required"
    else:
        app_logger.info("Query does not require escalation")
        state["should_escalate"] = False

    return state


def escalate_to_human(state: AgentState) -> AgentState:
    """
    Generate escalation message and prepare for human handoff

    Args:
        state: Current agent state

    Returns:
        Updated state with escalation response
    """
    app_logger.info("Escalating to human agent...")

    # Generate empathetic escalation message
    sentiment = state.get("sentiment", "Neutral")

    if sentiment == "Angry":
        message = (
            "I sincerely apologize for the frustration you're experiencing. "
            "Your concern is very important to us, and I'm connecting you with "
            "a specialized support representative who can provide immediate assistance. "
            "They will be with you shortly and have full context of your situation."
        )
    elif sentiment == "Negative":
        message = (
            "I understand your concern, and I want to ensure you receive the best possible assistance. "
            "I'm connecting you with a senior support specialist who can help resolve this issue. "
            "They'll have access to all the details we've discussed."
        )
    else:
        message = (
            "To ensure you receive the most accurate assistance for your inquiry, "
            "I'm connecting you with a specialized support representative. "
            "They'll be able to help you shortly."
        )

    # Add case reference
    message += f"\n\nCase Reference: {state.get('conversation_id', 'N/A')}"

    # Add estimated wait time (mock - would be real in production)
    message += "\n\nEstimated wait time: 2-5 minutes"

    state["response"] = message
    state["next_action"] = "escalate"

    return state
