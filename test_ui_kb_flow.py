"""
Test script to simulate Gradio UI KB results flow
This mimics what happens when you submit a query in the Gradio interface
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("GRADIO UI KB FLOW SIMULATION")
print("=" * 70)

print("\n[Step 1] Initialize database...")
try:
    from src.database import init_db

    init_db()
    print("  [OK] Database initialized")
except Exception as e:
    print(f"  [WARN] {e}")

print("\n[Step 2] Initialize agent...")
try:
    from src.main import get_customer_support_agent

    agent = get_customer_support_agent()
    print("  [OK] Agent initialized")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n[Step 3] Import format function...")
try:
    from src.ui.gradio_app import format_kb_results

    print("  [OK] Format function imported")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

print("\n[Step 4] Process query (simulating UI)...")
print("-" * 70)

test_query = "My app keeps crashing"
print(f"Query: '{test_query}'")
print()

try:
    # This is exactly what the Gradio UI does
    result = agent.process_query(query=test_query, user_id="test_user")

    print("\n" + "=" * 70)
    print("STEP 5: EXTRACT DATA (like Gradio UI does)")
    print("=" * 70)

    # Extract metadata (like Gradio UI)
    metadata = result.get("metadata", {})
    print(f"\nMetadata keys: {list(metadata.keys())}")

    # Extract KB results (like Gradio UI)
    kb_results = metadata.get("kb_results", [])
    print(f"\nKB Results extracted:")
    print(f"  - Type: {type(kb_results)}")
    print(f"  - Count: {len(kb_results)}")

    if kb_results:
        print(f"\nFirst KB result:")
        for key, value in kb_results[0].items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  - {key}: {value[:100]}...")
            else:
                print(f"  - {key}: {value}")

    print("\n" + "=" * 70)
    print("STEP 6: FORMAT KB RESULTS (like Gradio UI does)")
    print("=" * 70)

    # Format KB results (like Gradio UI)
    kb_html = format_kb_results(kb_results)

    print(f"\nFormatted HTML:")
    print(f"  - Length: {len(kb_html)} characters")
    print(f"  - Contains scores: {'%' in kb_html}")
    print(f"  - Contains 'N/A': {'N/A' in kb_html}")
    print(f"  - Contains 'No KB articles': {'No KB articles' in kb_html}")

    if kb_results:
        print(f"\n  - First 500 chars of HTML:")
        print(f"    {kb_html[:500]}...")

    print("\n" + "=" * 70)
    print("DIAGNOSIS")
    print("=" * 70)

    if len(kb_results) == 0:
        print("\n[ISSUE] KB results are empty!")
        print("  -> Check if knowledge base is initialized")
        print("  -> Run: python initialize_kb.py")
    elif "N/A" in kb_html:
        print("\n[ISSUE] HTML contains 'N/A' - data extraction problem!")
        print("  -> Check key names in format_kb_results()")
        print(
            "  -> KB results structure:",
            kb_results[0].keys() if kb_results else "empty",
        )
    elif "No KB articles" in kb_html:
        print("\n[ISSUE] format_kb_results received empty list!")
        print("  -> Data lost between agent and format function")
    else:
        print("\n[OK] Everything looks good!")
        print(f"  -> {len(kb_results)} KB results found and formatted")
        print(f"  -> HTML generated successfully")

    print("\n" + "=" * 70)
    print("FULL KB RESULTS DATA")
    print("=" * 70)
    for i, kb in enumerate(kb_results, 1):
        print(f"\n{i}. {kb}")

except Exception as e:
    print("\n" + "=" * 70)
    print("[ERROR] Test failed")
    print("=" * 70)
    print(f"\nError: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
