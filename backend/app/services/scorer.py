"""
Rule-based scoring engine. All scores are integers 0–100.

Dimensions
----------
ICP Fit       — how well the record matches Kantata's ideal customer profile
Pain Severity — how acute and urgent the expressed pain is
Purchase Intent — how likely the author is actively evaluating or switching tools
ABM Priority  — weighted composite of the three dimensions above

Every dimension returns a numeric score AND a list of reason strings that
explain every point added. These are stored on both the RedditRecord
(compact summary) and the Score row (full detail lists).
"""

from typing import Any

# ---------------------------------------------------------------------------
# ICP configuration
# ---------------------------------------------------------------------------

_TARGET_INDUSTRIES = frozenset({
    "Marketing Agency",
    "IT Services",
    "Management Consulting",
    "Architecture Engineering Construction",
    "Legal Services",
    "Accounting & Finance",
    "Software & Technology Services",
    "Staffing & Recruiting",
})

_TARGET_ROLES = frozenset({
    "PMO Director",
    "VP of Operations",
    "Resource Manager",
    "Finance Director",
    "Agency Owner",
    "Delivery Manager",
    "Practice Lead",
    "Project Manager",
})

_HIGH_VALUE_PAINS = frozenset({
    "Resource Utilization",
    "Project Profitability",
    "Forecasting Accuracy",
    "Real-time Visibility",
})

_PROFESSIONAL_SUBS = frozenset({
    "consulting", "itmanagers", "sysadmin", "msp", "marketing", "agile",
    "projectmanagement", "entrepreneur", "smallbusiness", "architecture",
    "legal", "accounting", "humanresources",
})

# ---------------------------------------------------------------------------
# Pain severity configuration
# ---------------------------------------------------------------------------

_HIGH_SEVERITY_PAINS = frozenset({
    "Resource Utilization",
    "Project Profitability",
    "Forecasting Accuracy",
})

_MED_SEVERITY_PAINS = frozenset({
    "Real-time Visibility",
    "Tool Fragmentation",
    "Scope Creep",
    "Team Burnout",
})

_URGENCY_PHRASES = [
    "killing us", "destroying our", "fire drill", "wheels coming off",
    "falling apart", "desperate", "can't keep up", "cannot keep up",
    "losing clients", "losing business", "breaking down", "in crisis",
    "no longer sustainable", "unsustainable",
]

# ---------------------------------------------------------------------------
# Purchase intent configuration
# ---------------------------------------------------------------------------

_STAGE_BASE: dict[str, int] = {
    "decision":     60,
    "frustration":  50,
    "consideration":45,
    "advocacy":     25,
    "awareness":    15,
}

_EVAL_PHRASES = [
    "evaluating", "comparing", "demo", "trial", "pilot",
    "proof of concept", "rfp", "shortlist", "vendor selection",
    "due diligence", "pricing", "getting quotes",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _body_text(record: dict[str, Any]) -> str:
    return " ".join(filter(None, [
        record.get("title") or "",
        record.get("body") or "",
    ])).lower()


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def _score_icp_fit(record: dict[str, Any]) -> tuple[int, list[str]]:
    """
    Max 100:
      +35  target industry match
      +15  adjacent/other industry present (mutually exclusive with +35)
      +25  target buyer role match
      +20  high-value pain points (up to 2 × +10)
      +10  professional services subreddit
      + 5  post type = post
      + 5  high engagement
    """
    score = 0
    reasons: list[str] = []
    industries: list[str] = record.get("industries") or []
    buyer_roles: list[str] = record.get("buyer_roles") or []
    pain_points: list[str] = record.get("pain_points") or []
    subreddit: str = (record.get("subreddit") or "").lower()

    # Industry
    target_inds = [i for i in industries if i in _TARGET_INDUSTRIES]
    if target_inds:
        score += 35
        reasons.append(f"Target industry: {target_inds[0]} (+35)")
    elif industries:
        score += 15
        reasons.append(f"Adjacent industry: {industries[0]} (+15)")

    # Buyer role
    target_roles = [r for r in buyer_roles if r in _TARGET_ROLES]
    if target_roles:
        score += 25
        reasons.append(f"Target buyer role: {target_roles[0]} (+25)")

    # High-value pain points (max 2)
    hv_pains = [p for p in pain_points if p in _HIGH_VALUE_PAINS][:2]
    if hv_pains:
        bonus = len(hv_pains) * 10
        score += bonus
        reasons.append(f"High-value pain point(s): {', '.join(hv_pains)} (+{bonus})")

    # Subreddit
    if subreddit in _PROFESSIONAL_SUBS:
        score += 10
        reasons.append(f"Professional services subreddit: r/{subreddit} (+10)")

    # Source type
    if record.get("source_type") == "post":
        score += 5
        reasons.append("Post type: post (+5)")

    # Engagement
    comments = record.get("num_comments") or 0
    votes = record.get("reddit_score") or 0
    if comments > 20 or votes > 50:
        score += 5
        reasons.append(f"High engagement: {comments} comments / {votes} upvotes (+5)")

    return _clamp(score), reasons


def _score_pain_severity(record: dict[str, Any]) -> tuple[int, list[str]]:
    """
    Max 100:
      +30 per high-severity pain (up to 2 × +30 = 60)
      +15 per medium-severity pain (up to 2 × +15 = 30)
      +10 urgency language detected
    """
    score = 0
    reasons: list[str] = []
    pain_points: list[str] = record.get("pain_points") or []
    text = _body_text(record)

    # High severity (max 2)
    high = [p for p in pain_points if p in _HIGH_SEVERITY_PAINS][:2]
    if high:
        bonus = len(high) * 30
        score += bonus
        reasons.append(f"High-severity pain(s): {', '.join(high)} (+{bonus})")

    # Medium severity (max 2)
    med = [p for p in pain_points if p in _MED_SEVERITY_PAINS][:2]
    if med:
        bonus = len(med) * 15
        score += bonus
        reasons.append(f"Medium-severity pain(s): {', '.join(med)} (+{bonus})")

    # Urgency language
    if any(phrase in text for phrase in _URGENCY_PHRASES):
        score += 10
        reasons.append("Urgency language detected (+10)")

    return _clamp(score), reasons


def _score_purchase_intent(record: dict[str, Any]) -> tuple[int, list[str]]:
    """
    Max 100:
      +60 / +50 / +45 / +25 / +15  intent stage base
      +20  any competitor mentioned
      +10  2+ competitors mentioned
      +10  evaluation language detected
    """
    score = 0
    reasons: list[str] = []
    intent_stage: str | None = record.get("intent_stage")
    competitors: list[str] = record.get("competitors") or []
    text = _body_text(record)

    # Stage base
    stage_pts = _STAGE_BASE.get(intent_stage or "", 0)
    if stage_pts:
        score += stage_pts
        reasons.append(f"Intent stage: {intent_stage} (+{stage_pts})")

    # Competitor mentions
    if competitors:
        score += 20
        reasons.append(f"Competitor mention: {competitors[0]} (+20)")
        if len(competitors) >= 2:
            score += 10
            reasons.append(f"Multiple competitors ({len(competitors)} total) (+10)")

    # Evaluation language
    if any(phrase in text for phrase in _EVAL_PHRASES):
        score += 10
        reasons.append("Evaluation language detected (+10)")

    return _clamp(score), reasons


def _score_abm_priority(
    icp: int, pain: int, intent: int
) -> tuple[int, list[str]]:
    """
    Weighted composite:  ICP × 0.35 + Pain × 0.30 + Intent × 0.35
    """
    raw = icp * 0.35 + pain * 0.30 + intent * 0.35
    abm = _clamp(round(raw))
    reasons = [
        f"ICP Fit ({icp}) × 0.35 + Pain Severity ({pain}) × 0.30 "
        f"+ Purchase Intent ({intent}) × 0.35 = {abm}"
    ]
    return abm, reasons


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score(record: dict[str, Any]) -> dict[str, Any]:
    """
    Compute all four scores for a tagged record dict.

    Returns a dict containing:
      icp_fit_score, pain_severity_score, purchase_intent_score, abm_priority_score
        — integer 0-100, stored on RedditRecord for fast filtering

      icp_fit_reasons, pain_severity_reasons,
      purchase_intent_reasons, abm_priority_reasons
        — list[str], stored on Score for full audit trail

      score_reasons
        — dict[str, str] compact per-dimension summary for the detail view
    """
    icp, icp_reasons       = _score_icp_fit(record)
    pain, pain_reasons     = _score_pain_severity(record)
    intent, intent_reasons = _score_purchase_intent(record)
    abm, abm_reasons       = _score_abm_priority(icp, pain, intent)

    return {
        "icp_fit_score":         icp,
        "pain_severity_score":   pain,
        "purchase_intent_score": intent,
        "abm_priority_score":    abm,
        # Detailed reason lists → written to scores table
        "icp_fit_reasons":         icp_reasons,
        "pain_severity_reasons":   pain_reasons,
        "purchase_intent_reasons": intent_reasons,
        "abm_priority_reasons":    abm_reasons,
        # Compact summary → written to reddit_records.score_reasons
        "score_reasons": {
            "icp_fit":        "; ".join(icp_reasons) or "No signal",
            "pain_severity":  "; ".join(pain_reasons) or "No signal",
            "purchase_intent":"; ".join(intent_reasons) or "No signal",
            "abm_priority":   abm_reasons[0],
        },
    }
