"""
tasks.py — Task definitions for the Meeting Decision Intelligence Environment.

Three tasks with increasing difficulty:
  1. Easy   — Meeting Summarization
  2. Medium — Action Item Extraction
  3. Hard   — Decision Intelligence (conflicting constraints)

Each task is a plain dictionary containing:
  - task_id, difficulty, task_description
  - meeting_transcript  (realistic scenario text)
  - expected_keywords   (for keyword-based grading)
  - expected_entities   (for entity/role matching — medium & hard)
  - decision_criteria   (for rule-based grading — hard only)
"""

from __future__ import annotations

from typing import Any, Dict, List

# ═══════════════════════════════════════════════════════════════════════════
# TASK 1 — Easy: Meeting Summarization
# ═══════════════════════════════════════════════════════════════════════════

EASY_TASK: Dict[str, Any] = {
    "task_id": "easy_summarization",
    "difficulty": "easy",
    "task_description": (
        "You are given a raw meeting transcript. Your goal is to produce a "
        "concise summary that captures the KEY TOPICS discussed. The summary "
        "should mention the main subjects, any decisions made, and the overall "
        "outcome of the meeting. Be specific — generic summaries score low."
    ),
    "meeting_transcript": (
        "Meeting: Q3 Product Planning Session\n"
        "Date: 2024-09-15\n"
        "Attendees: Sarah (PM), David (Engineering Lead), Maria (Design), Raj (QA)\n\n"
        "Sarah: Good morning everyone. Let's kick off our Q3 planning. We have three "
        "major initiatives to discuss: the mobile app redesign, the API performance "
        "improvements, and the new analytics dashboard.\n\n"
        "David: On the API side, we've identified several bottlenecks in our database "
        "queries. I estimate we can achieve a 40% latency reduction by implementing "
        "connection pooling and query optimization. We'll need about 3 sprints.\n\n"
        "Maria: For the mobile redesign, I've completed the wireframes based on the "
        "user research from last quarter. The main feedback was around navigation "
        "simplification and improved onboarding flow. We're proposing a bottom "
        "navigation bar and a 3-step onboarding tutorial.\n\n"
        "Raj: From QA perspective, we need to set up automated testing for the mobile "
        "app. Currently we only have 30% test coverage. I recommend reaching at least "
        "70% before the release.\n\n"
        "Sarah: Great points. What about the analytics dashboard?\n\n"
        "David: We can leverage our existing data pipeline. The main work will be "
        "building the frontend components and creating the aggregation queries. "
        "I suggest we use React with D3.js for the visualizations.\n\n"
        "Maria: I can have the dashboard mockups ready by next Friday.\n\n"
        "Sarah: Perfect. Let's prioritize the API improvements first since they "
        "affect all other projects. Mobile redesign second, and analytics dashboard "
        "third. Any objections?\n\n"
        "All: No objections.\n\n"
        "Sarah: Great. Let's schedule follow-up meetings for each initiative. "
        "Meeting adjourned."
    ),
    "expected_keywords": [
        "mobile", "redesign", "api", "performance", "analytics", "dashboard",
        "database", "latency", "wireframes", "navigation", "onboarding",
        "testing", "coverage", "prioritize", "q3", "planning",
        "react", "d3", "sprint", "bottleneck",
    ],
    "expected_entities": [],
    "decision_criteria": [],
}


# ═══════════════════════════════════════════════════════════════════════════
# TASK 2 — Medium: Action Item Extraction
# ═══════════════════════════════════════════════════════════════════════════

MEDIUM_TASK: Dict[str, Any] = {
    "task_id": "medium_action_items",
    "difficulty": "medium",
    "task_description": (
        "You are given a meeting transcript where responsibilities are assigned "
        "to specific people. Extract ALL action items. For each action item, "
        "clearly state: (1) WHO is responsible, (2) WHAT they need to do, and "
        "(3) any DEADLINE mentioned. Format each action item on its own line."
    ),
    "meeting_transcript": (
        "Meeting: Sprint Retrospective & Planning\n"
        "Date: 2024-10-01\n"
        "Attendees: Alex (Scrum Master), Priya (Backend Dev), Chen (Frontend Dev), "
        "Lisa (DevOps), Tom (Product Owner)\n\n"
        "Alex: Let's start with the retrospective. What went well last sprint?\n\n"
        "Priya: The new microservice architecture is working well. However, I still "
        "need to write the documentation for the payment API. I'll have that done "
        "by Friday October 4th.\n\n"
        "Chen: The new component library saved us a lot of time. But we discovered "
        "some accessibility issues. I'll run a full accessibility audit on the "
        "checkout flow and fix any WCAG violations by October 8th.\n\n"
        "Lisa: Our deployment pipeline had some flaky tests. I'm going to set up "
        "a new CI/CD pipeline with better retry logic and parallel test execution. "
        "Target completion is October 10th.\n\n"
        "Tom: From the product side, we need to finalize the pricing page copy. "
        "I'll coordinate with the marketing team and have the final copy ready "
        "by October 3rd. Also, Alex, can you schedule a demo for the stakeholders "
        "next Wednesday?\n\n"
        "Alex: Sure, I'll schedule the stakeholder demo for Wednesday October 9th. "
        "I'll also update the sprint board with the new user stories by end of day "
        "today.\n\n"
        "Priya: One more thing — the database migration script needs a review. "
        "Chen, can you pair with me on that tomorrow?\n\n"
        "Chen: Absolutely, let's block out 2 hours tomorrow morning for the "
        "migration review.\n\n"
        "Alex: Great. Let's make sure every action item has an owner and a date. "
        "Meeting adjourned."
    ),
    "expected_keywords": [
        "documentation", "payment", "api", "accessibility", "audit",
        "checkout", "wcag", "pipeline", "ci/cd", "retry", "pricing",
        "marketing", "demo", "stakeholder", "sprint", "board",
        "migration", "database", "review",
    ],
    "expected_entities": [
        {"name": "priya", "action": "documentation", "context": "payment api"},
        {"name": "priya", "action": "documentation", "context": "friday"},
        {"name": "chen", "action": "accessibility", "context": "checkout"},
        {"name": "chen", "action": "audit", "context": "wcag"},
        {"name": "chen", "action": "migration", "context": "review"},
        {"name": "lisa", "action": "pipeline", "context": "ci/cd"},
        {"name": "lisa", "action": "pipeline", "context": "retry"},
        {"name": "tom", "action": "pricing", "context": "marketing"},
        {"name": "tom", "action": "copy", "context": "pricing"},
        {"name": "alex", "action": "demo", "context": "stakeholder"},
        {"name": "alex", "action": "sprint board", "context": "user stories"},
    ],
    "decision_criteria": [],
}


# ═══════════════════════════════════════════════════════════════════════════
# TASK 3 — Hard: Decision Intelligence
# ═══════════════════════════════════════════════════════════════════════════

HARD_TASK: Dict[str, Any] = {
    "task_id": "hard_decision",
    "difficulty": "hard",
    "task_description": (
        "You are given a meeting transcript with CONFLICTING CONSTRAINTS "
        "involving budget limitations, tight deadlines, and competing priorities. "
        "You must:\n"
        "1. Identify the key constraints and trade-offs.\n"
        "2. Recommend an optimal decision with clear reasoning.\n"
        "3. Prioritize the options and justify your ranking.\n"
        "4. Address potential risks and propose mitigations.\n\n"
        "Your response should demonstrate structured thinking, consider all "
        "stakeholder perspectives, and provide a well-reasoned recommendation."
    ),
    "meeting_transcript": (
        "Meeting: Emergency Budget & Priority Alignment\n"
        "Date: 2024-11-05\n"
        "Attendees: VP Engineering (James), VP Sales (Karen), CFO (Michael), "
        "CTO (Nina), Head of Customer Success (Omar)\n\n"
        "James: We have a critical situation. Our remaining Q4 engineering budget "
        "is $150,000, but we have three competing priorities that collectively "
        "require $280,000. We need to make tough choices.\n\n"
        "Karen: Our biggest client, Acme Corp, is threatening to churn unless we "
        "deliver the custom reporting feature by December 15th. That's $2M in "
        "annual revenue at risk. The feature would cost $120,000 to build.\n\n"
        "Nina: We have a critical security vulnerability in our authentication "
        "system that was flagged in our latest penetration test. If exploited, "
        "it could expose user data for all 50,000 customers. The fix requires "
        "$80,000 and takes 3 weeks.\n\n"
        "Michael: From a financial perspective, we also committed to an "
        "infrastructure modernization project that would reduce our monthly cloud "
        "costs from $45,000 to $28,000 — saving $204,000 annually. That project "
        "costs $80,000.\n\n"
        "Omar: I want to flag that we've had 15 customer complaints about system "
        "slowness this month. The infrastructure project would also address "
        "these performance issues.\n\n"
        "James: So to summarize our options:\n"
        "  Option A: Custom reporting for Acme Corp — $120,000, deadline Dec 15\n"
        "  Option B: Security vulnerability fix — $80,000, urgent\n"
        "  Option C: Infrastructure modernization — $80,000, long-term savings\n\n"
        "With $150,000, we can do B+C ($160K — slightly over) or A only + partial B, "
        "but NOT all three.\n\n"
        "Karen: Losing Acme Corp would be devastating for our Q4 numbers.\n\n"
        "Nina: But a data breach could cost us millions in liability and destroy "
        "customer trust permanently.\n\n"
        "Michael: The infrastructure savings would pay for itself in 5 months.\n\n"
        "James: We need a recommendation that balances risk, revenue, and "
        "long-term value. What should we do?"
    ),
    "expected_keywords": [
        "security", "vulnerability", "priority", "budget", "constraint",
        "trade-off", "risk", "revenue", "acme", "reporting",
        "infrastructure", "modernization", "cost", "savings",
        "breach", "data", "customer", "trust", "deadline",
        "recommend", "decision", "mitigation", "prioritize",
    ],
    "expected_entities": [
        {"name": "james", "action": "engineering", "context": "budget"},
        {"name": "karen", "action": "sales", "context": "acme"},
        {"name": "nina", "action": "security", "context": "vulnerability"},
        {"name": "michael", "action": "finance", "context": "infrastructure"},
        {"name": "omar", "action": "customer success", "context": "performance"},
    ],
    "decision_criteria": [
        "security_first",       # Security should be top priority (safety > revenue)
        "risk_assessment",      # Mentions risk / liability / breach consequences
        "revenue_impact",       # Considers the $2M Acme Corp revenue
        "cost_benefit",         # Analyses cost vs. benefit for infra savings
        "phased_approach",      # Suggests phasing / sequencing / partial delivery
        "stakeholder_balance",  # Considers multiple stakeholder viewpoints
        "reasoning_quality",    # Structured, logical reasoning
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# ALL TASKS — ordered by difficulty
# ═══════════════════════════════════════════════════════════════════════════

ALL_TASKS: List[Dict[str, Any]] = [EASY_TASK, MEDIUM_TASK, HARD_TASK]


def get_task(index: int) -> Dict[str, Any]:
    """Return a task by its 0-based index. Raises IndexError if out of bounds."""
    return ALL_TASKS[index]


def get_task_count() -> int:
    """Return the number of available tasks."""
    return len(ALL_TASKS)
