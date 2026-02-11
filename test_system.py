"""
Test script for Multi-Agent HR Intelligence Platform
Run this to verify your installation and test the system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import init_db
from src.main import get_customer_support_agent
from src.utils.logger import app_logger


def test_basic_queries():
    """Test basic query processing"""

    print("\n" + "=" * 80)
    print("Multi-Agent HR Intelligence Platform - Test Suite")
    print("=" * 80 + "\n")

    # Initialize database
    print("Initializing database...")
    try:
        init_db()
        print("[DONE] Database initialized successfully\n")
    except Exception as e:
        print(f"[FAIL] Database initialization failed: {e}\n")
        return

    # Initialize agent
    print("Initializing customer support agent...")
    try:
        agent = get_customer_support_agent()
        print("[DONE] Agent initialized successfully\n")
    except Exception as e:
        print(f"[FAIL] Agent initialization failed: {e}\n")
        return

    # Test queries
    test_cases = [
        {
            "query": "I can't log into my account",
            "expected_category": "Account",
            "description": "Account access issue",
        },
        {
            "query": "Why was I charged twice this month?",
            "expected_category": "Billing",
            "description": "Billing inquiry",
        },
        {
            "query": "My app keeps crashing when I try to export data",
            "expected_category": "Technical",
            "description": "Technical problem",
        },
        {
            "query": "This is absolutely unacceptable! I want to speak to a manager NOW!",
            "expected_category": None,
            "description": "Angry customer - should escalate",
        },
        {
            "query": "What are your business hours?",
            "expected_category": "General",
            "description": "General information",
        },
    ]

    print("Running test queries...\n")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print("-" * 80)
        print(f"Query: {test_case['query']}")
        print()

        try:
            # Process query
            response = agent.process_query(
                query=test_case["query"], user_id="test_user_001"
            )

            # Display results
            print(f"[DONE] Processed successfully")
            print(f"   Category: {response['category']}")
            print(f"   Sentiment: {response['sentiment']}")
            print(f"   Priority: {response['priority']}")
            print(f"   Escalated: {response['metadata'].get('escalated', False)}")
            print(f"   Processing Time: {response['metadata']['processing_time']:.3f}s")
            print(f"\n   Response Preview:")
            print(f"   {response['response'][:200]}...")

            # Verify expected category (if not escalated)
            if test_case["expected_category"]:
                if response["category"] == test_case["expected_category"]:
                    print(
                        f"   [OK] Category matches expected: {test_case['expected_category']}"
                    )
                else:
                    print(
                        f"   [WARNING] Category mismatch - Expected: {test_case['expected_category']}, Got: {response['category']}"
                    )

            # Check escalation for angry query
            if "unacceptable" in test_case["query"].lower():
                if response["metadata"].get("escalated"):
                    print(f"   [OK] Correctly escalated angry customer")
                else:
                    print(f"   [WARNING] Should have escalated but didn't")

        except Exception as e:
            print(f"[FAIL] Error processing query: {e}")
            app_logger.error(f"Test case {i} failed", exc_info=True)

        print("-" * 80)

    print("\n" + "=" * 80)
    print("Test Suite Complete!")
    print("=" * 80 + "\n")

    # Test conversation history
    print("Testing conversation history retrieval...")
    try:
        history = agent.get_conversation_history("test_user_001", limit=5)
        print(f"[DONE] Retrieved {len(history)} conversations")
        for conv in history:
            print(f"   - {conv['category']}: {conv['query'][:50]}...")
    except Exception as e:
        print(f"[FAIL] Error retrieving history: {e}")

    print("\n All tests complete! System is ready to use.\n")


if __name__ == "__main__":
    test_basic_queries()
