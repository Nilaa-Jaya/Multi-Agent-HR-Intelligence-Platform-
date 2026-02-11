"""
Billing support response agent
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.logger import app_logger


# Billing support prompt
BILLING_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert billing and payment support agent with knowledge of invoices, subscriptions, refunds, and payment systems.

Customer Query: {query}

Customer Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Address billing concerns clearly and accurately
2. Explain charges, payment processes, or refund policies
3. If sentiment is negative, show empathy and apologize for inconvenience
4. Provide specific next steps for resolution
5. Reference relevant policies when appropriate
6. Escalate for refund requests or disputes if needed
7. Keep response professional and concise (200-300 words)

Response:"""
)


def handle_billing(state: AgentState) -> AgentState:
    """
    Generate billing support response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating billing response for: {state['query'][:50]}...")

    try:
        llm_manager = get_llm_manager()

        # Prepare conversation context
        context = ""
        if state.get("conversation_history"):
            context = "Previous conversation:\n"
            for msg in state["conversation_history"][-5:]:
                context += f"{msg['role'].capitalize()}: {msg['content']}\n"
            context += "\n"

        # Prepare knowledge base context
        kb_context = ""
        if state.get("kb_results"):
            kb_context = "Relevant billing policies:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            BILLING_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Billing response generated successfully")

        # Check if refund/dispute mentioned - may need escalation
        query_lower = state["query"].lower()
        if any(
            word in query_lower
            for word in ["refund", "dispute", "chargeback", "cancel subscription"]
        ):
            if not state.get("extra_metadata"):
                state["extra_metadata"] = {}
            state["extra_metadata"]["may_need_escalation"] = True

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_billing: {e}")
        state["response"] = (
            "I apologize for the inconvenience. For billing matters, please contact our billing department directly for immediate assistance."
        )
        state["should_escalate"] = True
        state["escalation_reason"] = "System error during response generation"
        return state
