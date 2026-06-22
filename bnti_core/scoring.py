"""Deterministic threat scoring shared by BNTI and WTI."""

import math

LLM_CATEGORY_WEIGHTS = {
    "military_conflict": 8.0,
    "terrorism": 7.0,
    "border_security": 5.0,
    "political_instability": 4.0,
    "humanitarian_crisis": 3.0,
    "diplomatic_tensions": 2.5,
    "trade_agreement": -2.0,
    "neutral": 0.0,
}

VALID_CATEGORIES = frozenset(LLM_CATEGORY_WEIGHTS.keys())

THRESHOLDS = {
    "STABLE": (1.0, 4.0),
    "ELEVATED": (4.0, 7.0),
    "CRITICAL": (7.0, 10.0),
}


def category_weights():
    return dict(LLM_CATEGORY_WEIGHTS)


def calculate_final_index(raw_score):
    """Map volume-normalized threat score to 1-10 index."""
    if raw_score <= 0:
        return 1.0
    scaled = raw_score / 5.0
    index = 1.0 + 9.0 * (1.0 - math.exp(-scaled * 1.2))
    return round(min(max(index, 1.0), 10.0), 2)


def status_from_index(index_value):
    if index_value > 7.0:
        return "CRITICAL"
    if index_value > 4.0:
        return "ELEVATED"
    return "STABLE"


def compute_country_score(events):
    """Average category weight for attributed events."""
    if not events:
        return 1.0, 0.0
    weights = [LLM_CATEGORY_WEIGHTS.get(e.get("category", "neutral"), 0.0) for e in events]
    raw = sum(weights) / len(weights)
    return calculate_final_index(raw), round(raw, 2)