"""
Test escalation logic to ensure it's not too aggressive
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.helpers import should_escalate, calculate_priority_score

print("=" * 70)
print("ESCALATION LOGIC TEST")
print("=" * 70)
print()

# Test cases that should NOT escalate
print("TEST CASES THAT SHOULD NOT ESCALATE:")
print("-" * 70)

test_cases_no_escalate = [
    {
        "query": "My app keeps crashing",
        "sentiment": "Negative",
        "category": "Technical",
        "attempt": 1,
        "expected_priority": 5,  # Base 3 + Negative 2 = 5
    },
    {
        "query": "I was charged twice",
        "sentiment": "Negative",
        "category": "Billing",
        "attempt": 1,
        "expected_priority": 5,  # Base 3 + Negative 2 = 5
    },
    {
        "query": "How do I reset my password",
        "sentiment": "Neutral",
        "category": "Account",
        "attempt": 1,
        "expected_priority": 3,  # Base 3 + Neutral 0 = 3
    },
    {
        "query": "The app crashed and I lost my work",
        "sentiment": "Negative",
        "category": "Technical",
        "attempt": 2,
        "expected_priority": 5,  # Base 3 + Negative 2 = 5
    },
]

for i, test in enumerate(test_cases_no_escalate, 1):
    priority = calculate_priority_score(
        sentiment=test["sentiment"],
        category=test["category"],
        is_repeat_query=(test["attempt"] > 1),
    )

    should_esc, reason = should_escalate(
        priority_score=priority,
        sentiment=test["sentiment"],
        attempt_count=test["attempt"],
        query=test["query"],
    )

    status = "[PASS]" if not should_esc else "[FAIL]"

    print(f"\n{i}. {test['query']}")
    print(
        f"   Sentiment: {test['sentiment']}, Priority: {priority}, Attempt: {test['attempt']}"
    )
    print(f"   Escalate: {should_esc}")
    if reason:
        print(f"   Reason: {reason}")
    print(f"   {status} - Should NOT escalate")

print("\n" + "=" * 70)
print("\nTEST CASES THAT SHOULD ESCALATE:")
print("-" * 70)

test_cases_escalate = [
    {
        "query": "This is UNACCEPTABLE! I want my money back NOW!",
        "sentiment": "Angry",
        "category": "Billing",
        "attempt": 1,
        "reason": "Angry sentiment + unacceptable keyword",
    },
    {
        "query": "My app keeps crashing",
        "sentiment": "Negative",
        "category": "Technical",
        "attempt": 3,
        "reason": "3rd attempt",
    },
    {
        "query": "I want to speak to a manager immediately",
        "sentiment": "Negative",
        "category": "General",
        "attempt": 1,
        "reason": "Manager keyword",
    },
    {
        "query": "I'm going to sue you for this!",
        "sentiment": "Angry",
        "category": "Billing",
        "attempt": 1,
        "reason": "Angry sentiment + sue keyword",
    },
]

for i, test in enumerate(test_cases_escalate, 1):
    priority = calculate_priority_score(
        sentiment=test["sentiment"],
        category=test["category"],
        is_repeat_query=(test["attempt"] > 1),
    )

    should_esc, reason = should_escalate(
        priority_score=priority,
        sentiment=test["sentiment"],
        attempt_count=test["attempt"],
        query=test["query"],
    )

    status = "[PASS]" if should_esc else "[FAIL]"

    print(f"\n{i}. {test['query']}")
    print(
        f"   Sentiment: {test['sentiment']}, Priority: {priority}, Attempt: {test['attempt']}"
    )
    print(f"   Escalate: {should_esc}")
    if reason:
        print(f"   Reason: {reason}")
    print(f"   Expected: {test['reason']}")
    print(f"   {status} - Should escalate")

print("\n" + "=" * 70)
print("\nSPECIFIC TEST: 'My app keeps crashing' (attempt 1)")
print("-" * 70)

priority = calculate_priority_score(sentiment="Negative", category="Technical")

should_esc, reason = should_escalate(
    priority_score=priority,
    sentiment="Negative",
    attempt_count=1,
    query="My app keeps crashing",
)

print(f"Query: 'My app keeps crashing'")
print(f"Sentiment: Negative")
print(f"Priority Score: {priority}")
print(f"Attempt Count: 1")
print(f"Should Escalate: {should_esc}")
print(f"Reason: {reason if reason else 'None'}")
print()

if not should_esc:
    print("[SUCCESS!] Query correctly NOT escalated")
else:
    print("[FAILED!] Query should NOT be escalated")

print("\n" + "=" * 70)
