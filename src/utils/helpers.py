"""
Utility helper functions
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import json


def generate_conversation_id() -> str:
    """Generate unique conversation ID"""
    timestamp = datetime.now().isoformat()
    hash_obj = hashlib.md5(timestamp.encode())
    return f"conv_{hash_obj.hexdigest()[:12]}"


def calculate_priority_score(
    sentiment: str, category: str, is_repeat_query: bool = False, is_vip: bool = False
) -> int:
    """
    Calculate priority score for query routing

    Priority Scale:
    1-3: Low (normal queries)
    4-6: Medium (negative sentiment)
    7-8: High (angry/urgent)
    9-10: Critical (angry + repeat/VIP)
    """
    score = 3  # Base score (reduced from 5)

    # Sentiment adjustments (reduced to be less aggressive)
    sentiment_scores = {
        "Negative": 2,  # Was 3
        "Angry": 3,  # Was 4
        "Neutral": 0,
        "Positive": 0,  # Was -1
    }
    score += sentiment_scores.get(sentiment, 0)

    # Category adjustments (removed to reduce score inflation)
    # Technical and Billing no longer get automatic bonus

    # Repeat query adjustment
    if is_repeat_query:
        score += 2

    # VIP adjustment
    if is_vip:
        score += 2

    # Clamp between 1 and 10
    return max(1, min(10, score))


def should_escalate(
    priority_score: int, sentiment: str, attempt_count: int = 1, query: str = ""
) -> tuple[bool, Optional[str]]:
    """
    Determine if query should be escalated to human agent

    Escalation triggers:
    1. Priority >= 8 (high severity)
    2. Sentiment is "Angry" (not just Negative)
    3. attempt_count >= 3 (multiple failed attempts)
    4. Specific escalation keywords ONLY: "lawsuit", "legal", "attorney",
       "sue", "refund immediately", "manager", "supervisor", "unacceptable"

    Do NOT escalate for:
    - Technical words like "crash", "error", "problem", "issue"
    - Priority 7 or below
    - First or second attempts
    - Negative sentiment alone (only Angry)

    Returns:
        tuple[bool, Optional[str]]: (should_escalate, escalation_reason)
    """
    reasons = []

    # High priority (8 or above, NOT 7)
    if priority_score >= 8:
        reasons.append("High priority score")

    # Angry sentiment (not just Negative)
    if sentiment == "Angry":
        reasons.append("Angry sentiment detected")

    # Multiple unsuccessful attempts (3+, not 2)
    if attempt_count >= 3:
        reasons.append("Multiple unsuccessful attempts")

    # Escalation keywords (be VERY selective)
    escalation_keywords = [
        "lawsuit",
        "legal",
        "attorney",
        "lawyer",
        "sue",
        "refund immediately",
        "speak to a manager",
        "speak to manager",
        "talk to a manager",
        "talk to manager",
        "contact supervisor",
        "unacceptable",
        "ridiculous",
        "demand refund",
        "escalate this",
    ]

    query_lower = query.lower()
    for keyword in escalation_keywords:
        if keyword in query_lower:
            reasons.append(f"Escalation keyword detected: {keyword}")
            break

    # Only escalate if we have STRONG reasons
    # Need either: Angry sentiment OR priority>=8 OR keywords OR attempts>=3
    should_escalate_flag = len(reasons) > 0

    escalation_reason = "; ".join(reasons) if should_escalate_flag else None

    return should_escalate_flag, escalation_reason


def format_response(
    response: str,
    category: str,
    sentiment: str,
    priority: int,
    conversation_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Format agent response with metadata"""
    return {
        "conversation_id": conversation_id,
        "response": response,
        "category": category,
        "sentiment": sentiment,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
    }


def parse_llm_category(raw_category: str) -> str:
    """Parse and standardize category from LLM response - HR Domain"""
    category_lower = raw_category.lower().strip()

    if "recruit" in category_lower or "hiring" in category_lower or "job" in category_lower or "interview" in category_lower:
        return "Recruitment"
    elif "payroll" in category_lower or "salary" in category_lower or "pay" in category_lower or "w-2" in category_lower or "w2" in category_lower:
        return "Payroll"
    elif "benefit" in category_lower or "insurance" in category_lower or "401k" in category_lower or "retirement" in category_lower:
        return "Benefits"
    elif "policy" in category_lower or "handbook" in category_lower or "code of conduct" in category_lower or "dress code" in category_lower:
        return "Policy"
    elif "leave" in category_lower or "vacation" in category_lower or "pto" in category_lower or "sick" in category_lower or "fmla" in category_lower:
        return "LeaveManagement"
    elif "performance" in category_lower or "review" in category_lower or "promotion" in category_lower or "goal" in category_lower:
        return "Performance"
    elif "general" in category_lower:
        return "General"
    else:
        return "General"


def parse_llm_sentiment(raw_sentiment: str) -> str:
    """Parse and standardize sentiment from LLM response"""
    sentiment_lower = raw_sentiment.lower()

    if (
        "negative" in sentiment_lower
        or "angry" in sentiment_lower
        or "frustrated" in sentiment_lower
    ):
        if (
            "very" in sentiment_lower
            or "extremely" in sentiment_lower
            or "angry" in sentiment_lower
        ):
            return "Angry"
        return "Negative"
    elif (
        "positive" in sentiment_lower
        or "happy" in sentiment_lower
        or "satisfied" in sentiment_lower
    ):
        return "Positive"
    else:
        return "Neutral"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


class Timer:
    """Simple timer context manager"""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, *args):
        self.end_time = datetime.now()
        self.elapsed = (self.end_time - self.start_time).total_seconds()

    def __str__(self):
        return f"{self.name}: {self.elapsed:.3f}s"
