"""
Sentiment analysis agent
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.helpers import parse_llm_sentiment, calculate_priority_score
from src.utils.logger import app_logger


# Sentiment analysis prompt
SENTIMENT_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert at analyzing customer sentiment and emotions.

Analyze the sentiment of the following customer query and classify it as ONE of these:
- Positive: Happy, satisfied, grateful, pleased
- Neutral: Informational, factual, calm
- Negative: Disappointed, frustrated, concerned, unhappy
- Angry: Very upset, furious, demanding, threatening

Consider the tone, word choice, and emotional indicators in the text.

Query: {query}

{context}

Respond with ONLY the sentiment label (Positive, Neutral, Negative, or Angry).
Sentiment:"""
)


def analyze_sentiment(state: AgentState) -> AgentState:
    """
    Analyze sentiment of customer query

    Args:
        state: Current agent state

    Returns:
        Updated state with sentiment and priority score
    """
    app_logger.info(f"Analyzing sentiment for query: {state['query'][:50]}...")

    try:
        llm_manager = get_llm_manager()

        # Prepare context
        context = ""
        if state.get("conversation_history"):
            context = "Conversation tone progression:\n"
            for msg in state["conversation_history"][-3:]:
                if msg["role"] == "user":
                    context += f"User: {msg['content'][:100]}\n"

        # Invoke LLM
        raw_sentiment = llm_manager.invoke_with_retry(
            SENTIMENT_PROMPT, {"query": state["query"], "context": context}
        )

        # Parse and standardize sentiment
        sentiment = parse_llm_sentiment(raw_sentiment)

        app_logger.info(f"Sentiment analyzed as: {sentiment}")

        # Calculate priority score
        user_context = state.get("user_context", {})
        is_repeat = user_context.get("is_repeat_query", False)
        is_vip = user_context.get("is_vip", False)

        priority_score = calculate_priority_score(
            sentiment=sentiment,
            category=state.get("category", "General"),
            is_repeat_query=is_repeat,
            is_vip=is_vip,
        )

        app_logger.info(f"Priority score calculated: {priority_score}")

        # Update state
        state["sentiment"] = sentiment
        state["priority_score"] = priority_score

        # Update metadata
        if not state.get("extra_metadata"):
            state["extra_metadata"] = {}
        state["extra_metadata"]["raw_sentiment"] = raw_sentiment

        return state

    except Exception as e:
        app_logger.error(f"Error in analyze_sentiment: {e}")
        # Fallback to Neutral sentiment
        state["sentiment"] = "Neutral"
        state["priority_score"] = 5
        return state
