"""
General HR support and specialized HR response agents
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.logger import app_logger


# General HR support prompt
GENERAL_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful HR support agent providing general assistance and information to employees.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide helpful, accurate HR information
2. Be friendly, professional, and supportive
3. Match the employee's emotional tone appropriately
4. Offer additional resources, portal links, or contact information
5. Guide employees to the right HR contacts when needed
6. Keep response concise and clear (150-250 words)

Response:"""
)


# Benefits specialist prompt
BENEFITS_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR Benefits specialist with deep knowledge of employee benefits, insurance, and retirement plans.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide clear guidance on benefits (health insurance, 401k, PTO, parental leave, wellness programs, perks)
2. Include specific enrollment steps, deadlines, and portal links (e.g., benefits.company.com)
3. Explain benefit options, eligibility, and qualifying life events
4. If the sentiment is confused or frustrated, break down complex benefits information simply
5. Address questions about enrollment, coverage, dependents, costs, and changes
6. Offer to connect them with benefits team at benefits@company.com for complex cases
7. Keep response helpful and informative (200-300 words)
8. Be especially clear about deadlines - missing enrollment windows has serious consequences

Response:"""
)


# Policy specialist prompt
POLICY_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR Policy specialist with deep knowledge of company policies, procedures, and the employee handbook.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide clear guidance on company policies (remote work, expenses, dress code, code of conduct, handbook)
2. Reference specific policy sections or handbook pages when applicable
3. Include step-by-step instructions for policy-related processes (expense reports, outside employment disclosure)
4. If the sentiment is negative, acknowledge concerns while maintaining policy guidelines
5. Address questions about workplace policies, conduct expectations, and compliance
6. For policy violations or ethics concerns, direct to ethics@company.com or anonymous hotline
7. Keep response professional and balanced (200-300 words)
8. Be clear about what's allowed vs. prohibited - no ambiguity

Response:"""
)


# Leave Management specialist prompt
LEAVE_MANAGEMENT_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR Leave Management specialist with deep knowledge of time-off policies, PTO, and leave programs.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide clear guidance on leave matters (vacation, PTO, sick leave, FMLA, parental leave, bereavement, other leave types)
2. Include specific steps for requesting time off, checking balances, and understanding accrual
3. Reference portal links (e.g., timeoff.company.com) and approval processes
4. If the sentiment is urgent or stressed, prioritize empathy - time off is often for important life events
5. Address questions about PTO balances, approval processes, blackout periods, and leave policies
6. For FMLA or complex medical leave, direct to leave specialist at leave@company.com
7. Keep response supportive and clear (200-300 words)
8. Be precise about deadlines, notice periods, and documentation requirements

Response:"""
)


# Performance specialist prompt
PERFORMANCE_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR Performance specialist with deep knowledge of performance management, career development, and employee growth.

Employee Query: {query}

Employee Sentiment: {sentiment}
Priority Level: {priority}

{context}

{kb_context}

Instructions:
1. Provide clear guidance on performance matters (reviews, goals, promotions, feedback, professional development, PIPs)
2. Include specific timelines, processes, and portal links (e.g., performance.company.com)
3. Be encouraging and growth-oriented - performance management is about development
4. If the sentiment is anxious or negative (especially about PIPs), be supportive while being honest
5. Address questions about review cycles, goal setting, promotion criteria, feedback culture, and career growth
6. For sensitive performance issues, recommend speaking with their manager or HR directly
7. Keep response motivating and actionable (200-300 words)
8. Emphasize resources available (training, mentorship, development programs)

Response:"""
)


def handle_general(state: AgentState) -> AgentState:
    """
    Generate general support response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating general response for: {state['query'][:50]}...")

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
            kb_context = "Relevant information:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            GENERAL_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("General response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_general: {e}")
        state["response"] = "Thank you for contacting us. How can I assist you today?"
        return state


def handle_benefits(state: AgentState) -> AgentState:
    """
    Generate benefits specialist response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating benefits response for: {state['query'][:50]}...")

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
            kb_context = "Benefits information:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            BENEFITS_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Benefits response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_benefits: {e}")
        state["response"] = (
            "I can help you with benefits questions. Please contact benefits@company.com or call ext. 2300 for immediate assistance."
        )
        return state


def handle_policy(state: AgentState) -> AgentState:
    """
    Generate policy specialist response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating policy response for: {state['query'][:50]}...")

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
            kb_context = "Policy information:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            POLICY_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Policy response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_policy: {e}")
        state["response"] = (
            "I can help you with policy questions. Please refer to the employee handbook at handbook.company.com or contact hr@company.com."
        )
        return state


def handle_leave_management(state: AgentState) -> AgentState:
    """
    Generate leave management specialist response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating leave management response for: {state['query'][:50]}...")

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
            kb_context = "Leave policy information:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            LEAVE_MANAGEMENT_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Leave management response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_leave_management: {e}")
        state["response"] = (
            "I can help you with leave requests. Please visit timeoff.company.com or contact leave@company.com for assistance."
        )
        return state


def handle_performance(state: AgentState) -> AgentState:
    """
    Generate performance specialist response

    Args:
        state: Current agent state

    Returns:
        Updated state with response
    """
    app_logger.info(f"Generating performance response for: {state['query'][:50]}...")

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
            kb_context = "Performance management resources:\n"
            for i, kb in enumerate(state["kb_results"][:2], 1):
                kb_context += (
                    f"{i}. {kb.get('title', 'N/A')}: {kb.get('content', '')[:200]}...\n"
                )
            kb_context += "\n"

        # Invoke LLM
        response = llm_manager.invoke_with_retry(
            PERFORMANCE_PROMPT,
            {
                "query": state["query"],
                "sentiment": state.get("sentiment", "Neutral"),
                "priority": state.get("priority_score", 5),
                "context": context,
                "kb_context": kb_context,
            },
        )

        app_logger.info("Performance response generated successfully")

        # Update state
        state["response"] = response
        state["next_action"] = "complete"

        return state

    except Exception as e:
        app_logger.error(f"Error in handle_performance: {e}")
        state["response"] = (
            "I can help you with performance and career development. Please contact your manager or visit performance.company.com."
        )
        return state
