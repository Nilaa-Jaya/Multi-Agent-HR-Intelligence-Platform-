"""
Test script to trace KB results flow through the system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("KB RESULTS DATA FLOW TEST")
print("=" * 70)

print("\n[Step 1] Initializing database...")
try:
    from src.database import init_db

    init_db()
    print("  [OK] Database initialized")
except Exception as e:
    print(f"  [WARN] Database init issue: {e}")
    print("  --> Continuing...")

print("\n[Step 2] Loading customer support agent...")
try:
    from src.main import get_customer_support_agent

    agent = get_customer_support_agent()
    print("  [OK] Agent loaded")
except Exception as e:
    print(f"  [FAIL] Agent loading failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n[Step 3] Processing test query...")
print("-" * 70)

test_query = "My app keeps crashing on startup"
print(f"Query: '{test_query}'")
print("\nLook for [MAIN DEBUG] and [UI DEBUG] logs below:")
print("-" * 70)

try:
    result = agent.process_query(query=test_query, user_id="test_user")

    print("\n" + "=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)

    print(f"\nResponse: {result.get('response', 'N/A')[:100]}...")
    print(f"Category: {result.get('category', 'N/A')}")
    print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"Priority: {result.get('priority', 'N/A')}")

    metadata = result.get("metadata", {})
    print(f"\nMetadata keys: {list(metadata.keys())}")

    kb_results = metadata.get("kb_results", [])
    print(f"\nKB Results in response: {len(kb_results)} items")

    if kb_results:
        print("\n" + "-" * 70)
        print("KB RESULTS DETAILS:")
        print("-" * 70)
        for i, kb in enumerate(kb_results, 1):
            print(f"\n{i}. Title: {kb.get('title', 'N/A')}")
            print(f"   Score: {kb.get('score', 0):.3f}")
            print(f"   Category: {kb.get('category', 'N/A')}")
            print(f"   Content: {kb.get('content', 'N/A')[:100]}...")
        print("-" * 70)
    else:
        print("\n[ISSUE] No KB results in final response metadata!")
        print("Check the debug logs above to see where data was lost.")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

    print("\nIf KB results are missing, check logs for:")
    print("  - [MAIN DEBUG] KB results from workflow: X items")
    print("  - [MAIN DEBUG] Passing X KB results to metadata")
    print("  - [UI DEBUG] KB results count: X")
    print("\nThese logs will show where the data is getting lost.")

except Exception as e:
    print("\n" + "=" * 70)
    print("[ERROR] Test failed")
    print("=" * 70)
    print(f"\nError: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
