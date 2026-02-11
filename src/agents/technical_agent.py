"""
Technical support response agent
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.logger import app_logger


# Technical support prompt
TECHNICAL_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert technical support agent with deep knowledge of software, hardware, and IT systems.

Customer Query: {query}

Customer Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide a clear, step-by-step technical solution
2. Use simple language while being technically accurate
3. If the sentiment is negative or angry, start with empathy
4. Include troubleshooting steps if applicable
5. Offer to escalate if the issue is complex
6. Keep response concise but comprehensive (200-300 words)

Response:"""
)


def handle_technical(state: AgentState) -> AgentState:
    """
    Generate technical support response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating technical response for: {state['query'][:50]}...")

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
            kb_context = "Relevant knowledge base articles:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            TECHNICAL_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Technical response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_technical: {e}")
        state["response"] = (
            "I apologize, but I'm experiencing technical difficulties. Please try again or contact support directly."
        )
        state["should_escalate"] = True
        state["escalation_reason"] = "System error during response generation"
        return state
