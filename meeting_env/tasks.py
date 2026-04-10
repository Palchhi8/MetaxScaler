"""
tasks.py — Task definitions for the Meeting Decision Intelligence Environment.

Four tasks with increasing difficulty:
  1. Easy    — Meeting Summarization
  2. Medium  — Action Item Extraction
  3. Hard    — Decision Intelligence (conflicting constraints)
  4. Extreme — Executive Triage & Sentiment

Each task is a plain dictionary containing:
  - task_id, difficulty, task_description
  - meeting_transcript  (realistic scenario text)
  - expected_keywords   (for keyword-based grading)
  - expected_entities   (for entity/role matching)
  - decision_criteria   (for rule-based grading)
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
        "concise summary that captures the KEY TOPICS discussed."
    ),
    "meeting_transcript": (
        "Meeting: Q3 Product Planning Session\n"
        "Sarah: Good morning. Let's discuss the mobile app redesign and API improvements.\n"
        "David: API bottlenecks are the priority. Maria: I have the mobile wireframes."
    ),
    "expected_keywords": ["mobile", "redesign", "api", "planning", "wireframes"],
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
        "Extract ALL action items. State WHO is responsible and WHAT they need to do."
    ),
    "meeting_transcript": (
        "Meeting: Sprint Planning\n"
        "Priya: I will write the payment documentation by Friday.\n"
        "Chen: I'll run the accessibility audit tomorrow."
    ),
    "expected_keywords": ["documentation", "audit", "accessibility", "payment"],
    "expected_entities": [
        {"name": "priya", "action": "documentation", "context": "payment"},
        {"name": "chen", "action": "audit", "context": "accessibility"},
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
        "Address conflicting constraints: $150k budget vs $280k needs. "
        "Options: A ($120k Acme feature), B ($80k Security fix), C ($80k Infra)."
    ),
    "meeting_transcript": (
        "James: We have $150k. Karen: Acme needs reporting ($120k) or they churn.\n"
        "Nina: Security vulnerability ($80k) is critical."
    ),
    "expected_keywords": ["budget", "security", "acme", "priority", "risk"],
    "expected_entities": [],
    "decision_criteria": ["security_first", "risk_assessment"],
}

# ═══════════════════════════════════════════════════════════════════════════
# TASK 4 — Extreme: Executive Triage
# ═══════════════════════════════════════════════════════════════════════════

TRIAGE_TASK: Dict[str, Any] = {
    "task_id": "executive_triage",
    "difficulty": "extreme",
    "task_description": (
        "Perform a sentiment analysis and triage the next steps. "
        "Evaluate the tone of the meeting and categorize the follow-up items "
        "by 'Urgent', 'High', 'Medium', and 'Low' priority with reasoning."
    ),
    "meeting_transcript": (
        "Meeting: Post-Mortem Outage Root Cause\n"
        "CEO: I am extremely disappointed. This 4-hour outage cost us $500k in sales. "
        "We cannot have this happen again. What went wrong?\n"
        "SRE Lead: It was a database failover test that went awry. We need better monitoring.\n"
        "Product: We also delayed the 'Free Credits' campaign because of this.\n"
        "CEO: I want a full report by EOD and a remediation plan by tomorrow morning."
    ),
    "expected_keywords": [
        "disappointed", "outage", "monitoring", "remediation", "urgent",
        "triage", "priority", "post-mortem", "failover", "database",
    ],
    "expected_entities": [
        {"name": "ceo", "action": "report", "context": "eod"},
        {"name": "sre", "action": "monitoring", "context": "database"},
    ],
    "decision_criteria": ["sentiment_analysis", "priority_classification"],
}

# ═══════════════════════════════════════════════════════════════════════════
# ALL TASKS
# ═══════════════════════════════════════════════════════════════════════════

ALL_TASKS: List[Dict[str, Any]] = [
    EASY_TASK, 
    MEDIUM_TASK, 
    HARD_TASK, 
    TRIAGE_TASK
]

def get_task(index: int) -> Dict[str, Any]:
    return ALL_TASKS[index]

def get_task_count() -> int:
    return len(ALL_TASKS)
