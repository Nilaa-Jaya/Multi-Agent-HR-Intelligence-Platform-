"""
Recruitment specialist response agent for HR inquiries
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.logger import app_logger


# Recruitment specialist prompt
RECRUITMENT_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR Recruitment specialist with deep knowledge of hiring processes, job applications, and talent acquisition.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide clear, actionable guidance on recruitment and hiring processes
2. Include specific steps, timelines, and portal links where applicable
3. If the sentiment is negative or frustrated, start with empathy and understanding
4. Address questions about: internal applications, interview processes, referrals, offer letters, onboarding, visa sponsorship
5. Offer to connect them with recruiting team for complex or urgent matters
6. Keep response professional and encouraging (200-300 words)
7. Be supportive and positive - recruitment is about opportunity and growth

Response:"""
)


def handle_recruitment(state: AgentState) -> AgentState:
    """
    Generate recruitment specialist response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating recruitment response for: {state['query'][:50]}...")

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

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            RECRUITMENT_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Recruitment response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_recruitment: {e}")
        state["response"] = (
            "I apologize, but I'm experiencing technical difficulties. "
            "Please contact recruiting@company.com or visit careers.company.com for assistance."
        )
        state["should_escalate"] = True
        state["escalation_reason"] = "System error during response generation"
        return state
