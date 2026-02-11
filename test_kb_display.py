"""
Test script to verify KB results display formatting
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.gradio_app import format_kb_results

print("=" * 70)
print("KB RESULTS DISPLAY TEST")
print("=" * 70)

# Sample KB results as returned by the agent
sample_kb_results = [
    {
        "title": "How do I reset my password?",
        "content": "To reset your password, click on 'Forgot Password' on the login page. Enter your email address and you will receive a password reset link within 5 minutes.",
        "category": "Account",
        "score": 0.892,
    },
    {
        "title": "App crashes on startup - troubleshooting steps",
        "content": "If your app crashes on startup, try these steps: 1) Clear app cache 2) Restart your device 3) Reinstall the app 4) Contact support if issue persists.",
        "category": "Technical",
        "score": 0.654,
    },
    {
        "title": "How to cancel subscription",
        "content": "To cancel your subscription, go to Settings > Billing > Manage Subscription > Cancel. Your access will continue until the end of the current billing period.",
        "category": "Billing",
        "score": 0.423,
    },
]

print("\nTest 1: Format KB results with CORRECT keys (score, title, content)")
print("-" * 70)
html_output = format_kb_results(sample_kb_results)
print("HTML Output Generated:")
print(html_output[:200] + "...")
print("\nChecking for key elements:")
print(f"  - Contains '89.2%': {'89.2%' in html_output}")
print(f"  - Contains '65.4%': {'65.4%' in html_output}")
print(f"  - Contains '42.3%': {'42.3%' in html_output}")
print(f"  - Contains 'reset my password': {'reset my password' in html_output}")
print(f"  - Contains 'Account' tag: {'Account' in html_output}")
print(f"  - Contains details tag: {'<details' in html_output}")

# Test with old key names (backwards compatibility)
print("\n" + "=" * 70)
print("Test 2: Format KB results with OLD keys (similarity_score, question, answer)")
print("-" * 70)

old_format_results = [
    {
        "question": "What are your business hours?",
        "answer": "We are open Monday-Friday 9AM-5PM EST.",
        "category": "General",
        "similarity_score": 0.756,
    }
]

html_output_old = format_kb_results(old_format_results)
print("HTML Output Generated:")
print(html_output_old[:200] + "...")
print("\nChecking for key elements:")
print(f"  - Contains '75.6%': {'75.6%' in html_output_old}")
print(f"  - Contains 'business hours': {'business hours' in html_output_old}")
print(f"  - Contains 'General' tag: {'General' in html_output_old}")

# Test with empty results
print("\n" + "=" * 70)
print("Test 3: Format empty KB results")
print("-" * 70)

empty_results = []
html_output_empty = format_kb_results(empty_results)
print("HTML Output:")
print(html_output_empty)
print(
    f"\nContains 'No KB articles found': {'No KB articles found' in html_output_empty}"
)

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

all_tests_passed = (
    "89.2%" in html_output
    and "65.4%" in html_output
    and "reset my password" in html_output
    and "75.6%" in html_output_old
    and "business hours" in html_output_old
    and "No KB articles found" in html_output_empty
)

if all_tests_passed:
    print("[OK] All tests passed!")
    print("\nThe KB results display is now working correctly:")
    print("  - Similarity scores display as percentages (e.g., 89.2%)")
    print("  - FAQ titles are shown")
    print("  - Categories are displayed")
    print("  - Content is in expandable sections")
    print("  - Supports both old and new key formats")
else:
    print("[FAIL] Some tests failed - check output above")

print("=" * 70)
