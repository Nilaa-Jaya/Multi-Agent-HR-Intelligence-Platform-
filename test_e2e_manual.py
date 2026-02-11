"""
End-to-End Testing - Multi-Agent HR Intelligence Platform
Tests complete user journey across all 7 HR categories
"""

from src.main import get_customer_support_agent
import time
from datetime import datetime

print("=" * 70)
print("E2E TESTING - Multi-Agent HR Intelligence Platform")
print("=" * 70)
print()

# Initialize agent
print("[*] Initializing agent...")
start_init = time.time()
agent = get_customer_support_agent()
init_time = time.time() - start_init
print(f"[OK] Agent initialized in {init_time:.2f}s\n")

# Test scenarios covering all 7 HR categories
test_scenarios = [
    # Recruitment (2 tests)
    {
        "category": "Recruitment",
        "query": "How do I apply for an internal position?",
        "expected_keywords": ["internal", "portal", "careers"],
        "should_escalate": False
    },
    {
        "category": "Recruitment",
        "query": "What is the interview process timeline?",
        "expected_keywords": ["week", "interview", "timeline"],
        "should_escalate": False
    },

    # Payroll (2 tests)
    {
        "category": "Payroll",
        "query": "When is payday?",
        "expected_keywords": ["friday", "bi-weekly", "direct deposit"],
        "should_escalate": False
    },
    {
        "category": "Payroll",
        "query": "My paycheck is missing 10 hours of overtime",
        "expected_keywords": ["payroll", "contact", "error"],
        "should_escalate": True  # Should escalate - payment error!
    },

    # Benefits (2 tests)
    {
        "category": "Benefits",
        "query": "How do I enroll in health insurance?",
        "expected_keywords": ["benefits", "enrollment", "31"],
        "should_escalate": False
    },
    {
        "category": "Benefits",
        "query": "What is the 401k matching policy?",
        "expected_keywords": ["401k", "match", "5%"],
        "should_escalate": False
    },

    # Policy (1 test)
    {
        "category": "Policy",
        "query": "What is the remote work policy?",
        "expected_keywords": ["remote", "hybrid", "office"],
        "should_escalate": False
    },

    # LeaveManagement (2 tests)
    {
        "category": "LeaveManagement",
        "query": "How do I request vacation time?",
        "expected_keywords": ["vacation", "pto", "timeoff"],
        "should_escalate": False
    },
    {
        "category": "LeaveManagement",
        "query": "What is the sick leave policy?",
        "expected_keywords": ["sick", "5 days", "leave"],
        "should_escalate": False
    },

    # Performance (1 test)
    {
        "category": "Performance",
        "query": "When are performance reviews conducted?",
        "expected_keywords": ["january", "annual", "review"],
        "should_escalate": False
    },

    # General (1 test)
    {
        "category": "General",
        "query": "Who do I contact for HR questions?",
        "expected_keywords": ["hr@company.com", "contact", "ext"],
        "should_escalate": False
    },
]

# Run tests
results = []
total_time = 0

print(f"[TEST] Running {len(test_scenarios)} E2E tests...\n")
print("-" * 70)

for i, test in enumerate(test_scenarios, 1):
    print(f"\n[Test {i}/{len(test_scenarios)}] {test['category']}")
    print(f"Query: \"{test['query']}\"")

    # Run query
    start = time.time()
    try:
        response = agent.process_query(
            query=test["query"],
            user_id=f"test_emp_{i:03d}"
        )
        elapsed = time.time() - start
        total_time += elapsed

        # Check results
        actual_category = response.get("category", "Unknown")
        actual_escalated = response.get("escalated", False)
        actual_response = response.get("response", "")

        # Verify category
        category_match = actual_category == test["category"]

        # Verify escalation
        escalation_match = actual_escalated == test["should_escalate"]

        # Verify keywords (at least 1 should be present)
        keywords_found = []
        for keyword in test["expected_keywords"]:
            if keyword.lower() in actual_response.lower():
                keywords_found.append(keyword)

        keywords_match = len(keywords_found) > 0

        # Overall pass/fail
        test_passed = category_match and escalation_match and keywords_match

        # Display results
        status = "[PASS]" if test_passed else "[FAIL]"
        print(f"Status: {status}")
        print(f"  Category: {actual_category} {'[OK]' if category_match else '[X] (expected ' + test['category'] + ')'}")
        print(f"  Escalated: {actual_escalated} {'[OK]' if escalation_match else '[X]'}")
        print(f"  Keywords: {len(keywords_found)}/{len(test['expected_keywords'])} found {keywords_found}")
        print(f"  Response time: {elapsed:.2f}s")
        print(f"  Response preview: {actual_response[:150]}...")

        results.append({
            "test_num": i,
            "category": test["category"],
            "query": test["query"],
            "passed": test_passed,
            "category_match": category_match,
            "escalation_match": escalation_match,
            "keywords_match": keywords_match,
            "response_time": elapsed
        })

    except Exception as e:
        print(f"[ERROR]: {str(e)}")
        results.append({
            "test_num": i,
            "category": test["category"],
            "query": test["query"],
            "passed": False,
            "error": str(e)
        })

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

# Calculate metrics
passed = sum(1 for r in results if r.get("passed", False))
failed = len(results) - passed
success_rate = (passed / len(results)) * 100 if results else 0
avg_time = total_time / len(results) if results else 0

print(f"\nTotal Tests: {len(results)}")
print(f"[+] Passed: {passed}")
print(f"[-] Failed: {failed}")
print(f"[*] Success Rate: {success_rate:.1f}%")
print(f"[*] Average Response Time: {avg_time:.2f}s")

# Category breakdown
print("\n[*] Category Breakdown:")
categories = {}
for r in results:
    cat = r["category"]
    if cat not in categories:
        categories[cat] = {"total": 0, "passed": 0}
    categories[cat]["total"] += 1
    if r.get("passed", False):
        categories[cat]["passed"] += 1

for cat, stats in sorted(categories.items()):
    rate = (stats["passed"] / stats["total"]) * 100
    print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")

# Overall verdict
print("\n" + "=" * 70)
if success_rate >= 90 and avg_time < 2.0:
    print("[SUCCESS] E2E TESTS PASSED! System is working correctly.")
elif success_rate >= 70:
    print("[WARNING] E2E TESTS PARTIALLY PASSED. Some issues need attention.")
else:
    print("[FAILED] E2E TESTS FAILED. System needs fixes.")
print("=" * 70)
