"""
Knowledge Base Retrieval Agent
Searches knowledge base for relevant FAQs before generating response
"""

from src.agents.state import AgentState
from src.knowledge_base.retriever import get_kb_retriever
from src.utils.logger import app_logger


def retrieve_from_kb(state: AgentState) -> AgentState:
    """
    Retrieve relevant FAQs from knowledge base

    Args:
        state: Current agent state

    Returns:
        Updated state with KB results
    """
    query = state.get("query", "")
    category = state.get("category", "General")

    app_logger.info(
        f"Retrieving from KB for category: {category}, query: {query[:50]}..."
    )

    try:
        # Get knowledge base retriever
        kb_retriever = get_kb_retriever()

        # Retrieve relevant FAQs
        # Get 3 results, filter by category for better relevance
        results = kb_retriever.retrieve(
            query=query,
            k=3,
            category=category,  # Filter by detected category
            min_score=0.3,  # Minimum similarity threshold
        )

        # Format results for agents
        kb_results = []
        for result in results:
            kb_results.append(
                {
                    "title": result.get("question", ""),
                    "content": result.get("answer", ""),
                    "category": result.get("category", ""),
                    "score": result.get("similarity_score", 0.0),
                }
            )

        # Update state
        state["kb_results"] = kb_results

        app_logger.info(f"Retrieved {len(kb_results)} FAQs from knowledge base")

        # Log top result if found
        if kb_results:
            top_result = kb_results[0]
            app_logger.info(
                f"Top result (score: {top_result['score']:.3f}): "
                f"{top_result['title'][:100]}..."
            )

        return state

    except Exception as e:
        app_logger.error(f"Error retrieving from knowledge base: {e}", exc_info=True)
        # Don't fail the workflow, just set empty results
        state["kb_results"] = []
        return state
