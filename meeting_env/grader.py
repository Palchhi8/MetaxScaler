"""
grader.py — Deterministic grading functions for the Meeting Environment.

All graders return a float reward in [0.0, 1.0] with partial scoring.

Grading strategies:
  - Easy:   keyword-based scoring
  - Medium: keyword scoring + entity/role matching
  - Hard:   keyword scoring + entity matching + decision-criteria rule checks
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


# ───────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation for matching."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s/]", " ", text)   # keep / for ci/cd etc.
    text = re.sub(r"\s+", " ", text)
    return text


def _keyword_score(response: str, keywords: List[str]) -> float:
    """Return fraction of *keywords* found in *response* (0.0–1.0)."""
    if not keywords:
        return 0.0
    norm = _normalise(response)
    hits = sum(1 for kw in keywords if kw.lower() in norm)
    return hits / len(keywords)


def _entity_score(response: str, entities: List[Dict[str, str]]) -> float:
    """Score based on how many (name, action) pairs appear in the response.

    Each entity dict has keys: name, action, context.
    A match counts if BOTH name AND action appear in the response.
    Bonus points if context also appears.
    """
    if not entities:
        return 0.0
    norm = _normalise(response)
    total_possible = len(entities) * 1.5  # 1.0 per name+action, 0.5 per context
    earned = 0.0
    for ent in entities:
        name_found = ent["name"].lower() in norm
        action_found = ent["action"].lower() in norm
        context_found = ent["context"].lower() in norm
        if name_found and action_found:
            earned += 1.0
            if context_found:
                earned += 0.5
    return min(earned / total_possible, 1.0)


def _decision_criteria_score(response: str, criteria: List[str]) -> float:
    """Rule-based scoring for decision intelligence tasks.

    Each criterion maps to a set of indicator phrases.  If at least one
    indicator is found the criterion is satisfied.
    """
    if not criteria:
        return 0.0

    norm = _normalise(response)

    criterion_indicators: Dict[str, List[str]] = {
        "security_first": [
            "security first", "security should", "prioritize security",
            "fix the vulnerability", "security is the top", "address the security",
            "security vulnerability must", "security takes priority",
            "most urgent", "critical vulnerability", "data breach",
        ],
        "risk_assessment": [
            "risk", "liability", "breach", "expose", "compliance",
            "worst case", "worst-case", "damage", "threat", "consequence",
        ],
        "revenue_impact": [
            "revenue", "2m", "2 million", "$2", "acme", "churn",
            "client retention", "annual revenue", "revenue at risk",
        ],
        "cost_benefit": [
            "cost", "saving", "roi", "return on investment", "pay for itself",
            "monthly cloud", "infrastructure saving", "long-term saving",
            "204", "28,000", "45,000",
        ],
        "phased_approach": [
            "phase", "sequenc", "partial", "incremental", "prioritize then",
            "first then", "after that", "follow up", "negotiate",
            "timeline", "defer", "postpone", "stagger",
        ],
        "stakeholder_balance": [
            "stakeholder", "perspective", "james", "karen", "nina",
            "michael", "omar", "viewpoint", "balance", "all parties",
            "engineering", "sales", "cto", "cfo",
        ],
        "reasoning_quality": [
            "because", "therefore", "recommend", "conclusion", "rationale",
            "analysis", "considering", "given that", "weigh", "trade-off",
            "tradeoff", "on balance", "decision",
        ],
    }

    hits = 0
    for criterion in criteria:
        indicators = criterion_indicators.get(criterion, [])
        if any(ind in norm for ind in indicators):
            hits += 1

    return hits / len(criteria)


# ───────────────────────────────────────────────────────────────────────────
# Public grading API
# ───────────────────────────────────────────────────────────────────────────

def grade_response(
    response: str,
    task: Dict[str, Any],
) -> Tuple[float, str]:
    """Grade an agent response against the given task definition.

    Args:
        response: The agent's textual answer.
        task: Task dict from tasks.py (must contain expected_keywords etc.).

    Returns:
        (reward, feedback) where reward ∈ [0.0, 1.0].
    """
    # Penalise empty / very short responses
    if not response or len(response.strip()) < 10:
        return 0.0, "Response is empty or too short. No credit awarded."

    difficulty = task["difficulty"]
    feedback_parts: List[str] = []

    # ── Keyword score (all difficulties) ──────────────────────────────
    kw_score = _keyword_score(response, task.get("expected_keywords", []))
    feedback_parts.append(f"Keyword coverage: {kw_score:.2f}")

    if difficulty == "easy":
        # Easy: 100 % keyword-based
        reward = kw_score
        feedback_parts.append(f"Final score (keyword only): {reward:.2f}")

    elif difficulty == "medium":
        # Medium: 40 % keywords + 60 % entity matching
        ent_score = _entity_score(response, task.get("expected_entities", []))
        reward = 0.40 * kw_score + 0.60 * ent_score
        feedback_parts.append(f"Entity matching: {ent_score:.2f}")
        feedback_parts.append(f"Final score (40%kw + 60%ent): {reward:.2f}")

    elif difficulty == "hard":
        # Hard: 20 % keywords + 30 % entities + 50 % decision criteria
        ent_score = _entity_score(response, task.get("expected_entities", []))
        dec_score = _decision_criteria_score(
            response, task.get("decision_criteria", [])
        )
        reward = 0.20 * kw_score + 0.30 * ent_score + 0.50 * dec_score
        feedback_parts.append(f"Entity matching: {ent_score:.2f}")
        feedback_parts.append(f"Decision criteria: {dec_score:.2f}")
        feedback_parts.append(f"Final score (20%kw + 30%ent + 50%dec): {reward:.2f}")

    else:
        reward = 0.0
        feedback_parts.append(f"Unknown difficulty '{difficulty}'. Score: 0.0")

    # Clamp to [0.0, 1.0]
    reward = max(0.0, min(1.0, round(reward, 4)))
    feedback = " | ".join(feedback_parts)
    return reward, feedback
