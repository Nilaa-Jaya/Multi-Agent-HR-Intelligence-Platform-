"""
Example usage of Multi-Agent HR Intelligence Platform
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import init_db
from src.main import get_customer_support_agent


def main():
    """Main example function"""

    print("\n" + "=" * 80)
    print("Welcome to Multi-Agent HR Intelligence Platform - Customer Support Agent")
    print("=" * 80 + "\n")

    # Initialize database (first time only)
    print("Initializing system...")
    init_db()

    # Get agent instance
    agent = get_customer_support_agent()
    print("Agent ready!\n")

    # Example 1: Simple query
    print("\n--- Example 1: Technical Query ---")
    response = agent.process_query(
        query="My app keeps crashing when I try to save files", user_id="user_john"
    )

    print(f"Category: {response['category']}")
    print(f"Sentiment: {response['sentiment']}")
    print(f"Response:\n{response['response']}\n")

    # Example 2: Billing query
    print("\n--- Example 2: Billing Query ---")
    response = agent.process_query(
        query="I was charged $50 but my subscription should only be $30",
        user_id="user_sarah",
    )

    print(f"Category: {response['category']}")
    print(f"Sentiment: {response['sentiment']}")
    print(f"Response:\n{response['response']}\n")

    # Example 3: Angry customer (should escalate)
    print("\n--- Example 3: Escalation Case ---")
    response = agent.process_query(
        query="This is ridiculous! I've been waiting for hours and nobody has helped me!",
        user_id="user_angry",
    )

    print(f"Category: {response['category']}")
    print(f"Sentiment: {response['sentiment']}")
    print(f"Escalated: {response['metadata'].get('escalated', False)}")
    print(f"Response:\n{response['response']}\n")

    # Example 4: Get conversation history
    print("\n--- Example 4: Conversation History ---")
    history = agent.get_conversation_history("user_john", limit=5)
    print(f"Found {len(history)} conversations for user_john:")
    for conv in history:
        print(f"  - [{conv['category']}] {conv['query'][:60]}...")

    print("\n" + "=" * 80)
    print("Examples complete! Check the code to see how it works.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
