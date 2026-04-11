"""
grader.py — Deterministic grading functions for the Meeting Environment.

All graders return a float reward STRICTLY in (0, 1) — never 0.0 or 1.0.

Grading strategies:
  - Easy:   keyword-based scoring
  - Medium: keyword scoring + entity/role matching
  - Hard:   keyword scoring + entity matching + decision-criteria rule checks
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


# ───────────────────────────────────────────────────────────────────────────
# Constants — strict score bounds
# ───────────────────────────────────────────────────────────────────────────

MIN_SCORE = 0.05  # Floor: never return 0.0
MAX_SCORE = 0.95  # Ceiling: never return 1.0


def _clamp(score: float) -> float:
    """Clamp a score to the strict open interval (0, 1)."""
    return max(MIN_SCORE, min(MAX_SCORE, round(score, 4)))


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
        "sentiment_analysis": [
            "sentiment", "tone", "atmosphere", "disappointed", "urgent",
            "critical", "stress", "frustrat", "serious", "gravity",
        ],
        "priority_classification": [
            "priority", "triage", "categorize", "urgent", "high", "medium", "low",
            "rank", "classify", "ordering", "sequence",
        ],
    }

    hits = 0
    for criterion in criteria:
        indicators = criterion_indicators.get(criterion, [])
        if any(ind in _normalise(response) for ind in indicators):
            hits += 1

    return hits / len(criteria)


# ───────────────────────────────────────────────────────────────────────────
# Public grading API
# ───────────────────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────
# Named Grader Functions (required for validation)
# ───────────────────────────────────────────────────────────────────────────

def keyword_grader(response: str, task: Dict[str, Any]) -> Tuple[float, str]:
    """Easy task: pure keyword matching."""
    if not response or len(response.strip()) < 10:
        return MIN_SCORE, f"Response is empty or too short. Minimal score: {MIN_SCORE}"
    kw_score = _keyword_score(response, task.get("expected_keywords", []))
    reward = _clamp(kw_score)
    return reward, f"Keyword coverage: {kw_score:.2f} | Final score: {reward:.2f}"

def entity_grader(response: str, task: Dict[str, Any]) -> Tuple[float, str]:
    """Medium task: keywords + entities."""
    if not response or len(response.strip()) < 10:
        return MIN_SCORE, f"Response is empty or too short. Minimal score: {MIN_SCORE}"
    kw_score = _keyword_score(response, task.get("expected_keywords", []))
    ent_score = _entity_score(response, task.get("expected_entities", []))
    reward = _clamp(0.40 * kw_score + 0.60 * ent_score)
    return reward, f"Keywords: {kw_score:.2f} | Entities: {ent_score:.2f} | Final: {reward:.2f}"

def decision_grader(response: str, task: Dict[str, Any]) -> Tuple[float, str]:
    """Hard task: keywords + entities + decision criteria."""
    if not response or len(response.strip()) < 10:
        return MIN_SCORE, f"Response is empty or too short. Minimal score: {MIN_SCORE}"
    kw_score = _keyword_score(response, task.get("expected_keywords", []))
    ent_score = _entity_score(response, task.get("expected_entities", []))
    dec_score = _decision_criteria_score(response, task.get("decision_criteria", []))
    reward = _clamp(0.20 * kw_score + 0.30 * ent_score + 0.50 * dec_score)
    return reward, f"Keywords: {kw_score:.2f} | Entities: {ent_score:.2f} | Decisions: {dec_score:.2f} | Final: {reward:.2f}"

def triage_grader(response: str, task: Dict[str, Any]) -> Tuple[float, str]:
    """Extreme task: heavy weighting on triage criteria."""
    if not response or len(response.strip()) < 10:
        return MIN_SCORE, f"Response is empty or too short. Minimal score: {MIN_SCORE}"
    kw_score = _keyword_score(response, task.get("expected_keywords", []))
    ent_score = _entity_score(response, task.get("expected_entities", []))
    dec_score = _decision_criteria_score(response, task.get("decision_criteria", []))
    reward = _clamp(0.10 * kw_score + 0.30 * ent_score + 0.60 * dec_score)
    return reward, f"Keywords: {kw_score:.2f} | Entities: {ent_score:.2f} | Triage: {dec_score:.2f} | Final: {reward:.2f}"

def grade_response(
    response: str,
    task: Dict[str, Any],
) -> Tuple[float, str]:
    """Main dispatcher: select grader by name from task."""
    grader_name = task.get("grader", "keyword_grader")
    
    graders = {
        "keyword_grader": keyword_grader,
        "entity_grader": entity_grader,
        "decision_grader": decision_grader,
        "triage_grader": triage_grader,
    }
    
    grader = graders.get(grader_name, keyword_grader)
    return grader(response, task)
