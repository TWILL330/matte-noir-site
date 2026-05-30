from typing import Any


def score(record: dict[str, Any]) -> dict[str, Any]:
    """
    Compute rule-based scores for a tagged record.
    Returns a dict with: icp_fit_score, pain_severity_score,
    purchase_intent_score, abm_priority_score, score_reasons.
    All scores are floats in the range 0.0–1.0.
    """
    raise NotImplementedError
