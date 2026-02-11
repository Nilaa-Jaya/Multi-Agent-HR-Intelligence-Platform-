"""
Query categorization agent
"""

from langchain_core.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.agents.llm_manager import get_llm_manager
from src.utils.helpers import parse_llm_category
from src.utils.logger import app_logger


# Categorization prompt - HR Domain
CATEGORIZATION_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert HR query classifier for employee support.

Categorize the following employee query into ONE of these categories:

- Recruitment: Job applications, internal positions, hiring process, interviews, candidate screening, referrals, onboarding, offer letters, visa sponsorship
- Payroll: Salary, paychecks, pay schedule, direct deposit, tax withholdings, W-2 forms, pay slips, overtime, compensation, payment errors
- Benefits: Health insurance, 401(k), retirement plans, PTO accrual, parental leave, wellness programs, employee perks, benefit enrollment, life insurance, disability
- Policy: Company policies, employee handbook, remote work policy, dress code, code of conduct, expense reports, outside employment, workplace guidelines
- LeaveManagement: Vacation requests, PTO, sick leave, FMLA, bereavement leave, jury duty, military leave, sabbatical, leave of absence, time-off balance
- Performance: Performance reviews, annual goals, promotions, feedback, professional development, PIPs, career growth, mentorship, training
- General: General HR inquiries, employee portal access, HR contacts, onboarding process, company information, miscellaneous HR questions

Query: {query}

{context}

Respond with ONLY the category name (Recruitment, Payroll, Benefits, Policy, LeaveManagement, Performance, or General).
Category:"""
)


def categorize_query(state: AgentState) -> AgentState:
    """
    Categorize customer query

    Args:
        state: Current agent state

    Returns:
        Updated state with category
    """
    app_logger.info(f"Categorizing query: {state['query'][:50]}...")

    try:
        llm_manager = get_llm_manager()

        # Prepare context
        context = ""
        if state.get("conversation_history"):
            context = "Previous conversation context:\n"
            for msg in state["conversation_history"][-3:]:
                context += f"{msg['role']}: {msg['content'][:100]}\n"

        # Invoke LLM
        raw_category = llm_manager.invoke_with_retry(
            CATEGORIZATION_PROMPT, {"query": state["query"], "context": context}
        )

        # Parse and standardize category
        category = parse_llm_category(raw_category)

        app_logger.info(f"Query categorized as: {category}")

        # Update state
        state["category"] = category

        # Update metadata
        if not state.get("extra_metadata"):
            state["extra_metadata"] = {}
        state["extra_metadata"]["raw_category"] = raw_category

        return state

    except Exception as e:
        app_logger.error(f"Error in categorize_query: {e}")
        # Fallback to General category
        state["category"] = "General"
        return state
