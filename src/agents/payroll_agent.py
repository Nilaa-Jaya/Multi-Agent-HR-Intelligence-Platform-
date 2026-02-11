"""
Payroll specialist response agent for HR inquiries
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.logger import app_logger


# Payroll specialist prompt
PAYROLL_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR Payroll specialist with deep knowledge of compensation, tax withholdings, and payroll processes.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide clear, accurate guidance on payroll matters (pay schedules, direct deposit, tax forms, deductions)
2. Include specific steps, deadlines, and portal links (e.g., payroll.company.com)
3. If the sentiment is negative or urgent (especially payment errors), prioritize empathy and urgency
4. For SENSITIVE inquiries about specific salary amounts or personal compensation, recommend contacting payroll@company.com directly
5. Address questions about: paychecks, pay slips, W-2 forms, direct deposit, tax withholdings, overtime, payment errors
6. Offer to escalate to payroll team for payment discrepancies or urgent issues
7. Keep response professional and reassuring (200-300 words)
8. Be precise with numbers, dates, and deadlines - accuracy is critical in payroll

IMPORTANT: For specific salary inquiries or payment disputes, always escalate to the payroll team.

Response:"""
)


def handle_payroll(state: AgentState) -> AgentState:
    """
    Generate payroll specialist response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating payroll response for: {state['query'][:50]}...")

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
            kb_context = "Relevant HR knowledge base articles:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Check for payment error keywords - auto-escalate
        query_lower = state["query"].lower()
        if any(keyword in query_lower for keyword in ["incorrect", "wrong", "missing", "error", "not paid", "didn't receive"]):
            state["should_escalate"] = True
            state["escalation_reason"] = "Potential payroll error requiring immediate attention"
            app_logger.info("Auto-escalating potential payroll error")

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            PAYROLL_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Payroll response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_payroll: {e}")
        state["response"] = (
            "I apologize, but I'm experiencing technical difficulties. "
            "For urgent payroll matters, please contact payroll@company.com or call ext. 2200 immediately."
        )
        state["should_escalate"] = True
        state["escalation_reason"] = "System error during response generation"
        return state
