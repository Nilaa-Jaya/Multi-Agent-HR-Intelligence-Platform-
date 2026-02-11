"""
Multi-Agent HR Workflow Orchestrator using LangGraph
Version: 3.0.0
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from src.agents.state import AgentState
from src.agents.categorizer import categorize_query
from src.agents.sentiment_analyzer import analyze_sentiment
from src.agents.kb_retrieval import retrieve_from_kb
from src.agents.recruitment_agent import handle_recruitment
from src.agents.payroll_agent import handle_payroll
from src.agents.general_agent import (
    handle_general,
    handle_benefits,
    handle_policy,
    handle_leave_management,
    handle_performance,
)
from src.agents.escalation_agent import check_escalation, escalate_to_human
from src.utils.logger import app_logger


def route_query(
    state: AgentState,
) -> Literal[
    "escalate",
    "recruitment",
    "payroll",
    "benefits",
    "policy",
    "leave_management",
    "performance",
    "general",
]:
    """
    Route query based on escalation check and HR category

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    # First check if escalation is needed
    if state.get("should_escalate", False):
        app_logger.info("Routing to escalation")
        return "escalate"

    # Route based on HR category
    category = state.get("category", "General")

    route_map = {
        "Recruitment": "recruitment",
        "Payroll": "payroll",
        "Benefits": "benefits",
        "Policy": "policy",
        "LeaveManagement": "leave_management",
        "Performance": "performance",
        "General": "general",
    }

    route = route_map.get(category, "general")
    app_logger.info(f"Routing to {route} agent (category: {category})")
    return route


def create_workflow() -> StateGraph:
    """
    Create the HR support workflow graph

    Returns:
        Compiled StateGraph workflow
    """
    app_logger.info("Creating HR support workflow...")

    # Initialize workflow
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("categorize", categorize_query)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("retrieve_kb", retrieve_from_kb)
    workflow.add_node("check_escalation", check_escalation)

    # HR specialist agents
    workflow.add_node("recruitment", handle_recruitment)
    workflow.add_node("payroll", handle_payroll)
    workflow.add_node("benefits", handle_benefits)
    workflow.add_node("policy", handle_policy)
    workflow.add_node("leave_management", handle_leave_management)
    workflow.add_node("performance", handle_performance)
    workflow.add_node("general", handle_general)

    # Escalation node
    workflow.add_node("escalate", escalate_to_human)

    # Set entry point
    workflow.set_entry_point("categorize")

    # Add edges
    workflow.add_edge("categorize", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "retrieve_kb")
    workflow.add_edge("retrieve_kb", "check_escalation")

    # Add conditional routing after escalation check
    workflow.add_conditional_edges(
        "check_escalation",
        route_query,
        {
            "recruitment": "recruitment",
            "payroll": "payroll",
            "benefits": "benefits",
            "policy": "policy",
            "leave_management": "leave_management",
            "performance": "performance",
            "general": "general",
            "escalate": "escalate",
        },
    )

    # All response nodes lead to END
    workflow.add_edge("recruitment", END)
    workflow.add_edge("payroll", END)
    workflow.add_edge("benefits", END)
    workflow.add_edge("policy", END)
    workflow.add_edge("leave_management", END)
    workflow.add_edge("performance", END)
    workflow.add_edge("general", END)
    workflow.add_edge("escalate", END)

    # Compile workflow
    app_logger.info("HR workflow created successfully")
    return workflow.compile()


# Global workflow instance
_workflow = None


def get_workflow():
    """Get or create workflow singleton"""
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow
