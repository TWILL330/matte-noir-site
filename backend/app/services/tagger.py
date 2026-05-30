"""
Rule-based tagger for the five enrichment dimensions.

Uses word-boundary regex matching so "asana" never matches "organizational"
and "jira" never matches "jiraffe". All matching is case-insensitive.
"""

import re
from typing import Any

# ---------------------------------------------------------------------------
# Keyword tables
# Each entry: {canonical_term: [keyword, ...]}
# All keywords are matched case-insensitively with word boundaries.
# ---------------------------------------------------------------------------

_INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "Marketing Agency": [
        "marketing agency", "ad agency", "creative agency", "digital agency",
        "advertising agency", "media agency", "branding agency",
    ],
    "IT Services": [
        "managed services", "managed service provider", "msp",
        "it consulting", "systems integrator", "it services",
        "technology services", "tech consulting",
    ],
    "Management Consulting": [
        "consulting firm", "management consulting", "strategy consulting",
        "consultancy", "professional services firm", "advisory firm",
        "management consultancy",
    ],
    "Architecture Engineering Construction": [
        "architecture firm", "engineering firm", "construction firm",
        "design firm", "structural engineering", "civil engineering", "aec",
    ],
    "Legal Services": [
        "law firm", "legal practice", "attorneys", "litigation",
        "legal services", "solicitors", "legal advisory",
    ],
    "Accounting & Finance": [
        "cpa firm", "accounting firm", "financial advisory", "audit firm",
        "tax firm", "bookkeeping", "financial services",
    ],
    "Software & Technology Services": [
        "software development", "development shop", "dev shop",
        "software consulting", "tech startup",
    ],
    "Staffing & Recruiting": [
        "staffing agency", "recruiting firm", "talent agency", "headhunting",
    ],
    "PR & Communications": [
        "public relations", "pr firm", "communications agency",
    ],
    "Research & Analytics": [
        "market research", "data analytics", "insights firm", "research firm",
    ],
}

# Subreddit name → industry (fast O(1) lookup, no regex needed)
_SUB_INDUSTRY: dict[str, str] = {
    "consulting":       "Management Consulting",
    "itmanagers":       "IT Services",
    "sysadmin":         "IT Services",
    "msp":              "IT Services",
    "marketing":        "Marketing Agency",
    "agile":            "IT Services",
    "projectmanagement":"Management Consulting",
    "entrepreneur":     "Management Consulting",
    "smallbusiness":    "Management Consulting",
    "architecture":     "Architecture Engineering Construction",
    "legal":            "Legal Services",
    "accounting":       "Accounting & Finance",
    "humanresources":   "Management Consulting",
}

_BUYER_ROLE_KEYWORDS: dict[str, list[str]] = {
    "PMO Director":    ["pmo director", "head of pmo", "director of project management", "vp of pmo"],
    "VP of Operations":["coo", "chief operating officer", "vp of operations", "operations director", "vp ops"],
    "Project Manager": ["project manager", "engagement manager", "delivery manager", "project lead", "project management"],
    "Resource Manager":["resource manager", "resource planner", "capacity planner", "staffing manager", "workforce manager"],
    "Finance Director":["cfo", "chief financial officer", "finance director", "financial controller", "vp of finance"],
    "IT Manager":      ["it manager", "it director", "cto", "vp of it", "technology manager"],
    "Agency Owner":    ["agency owner", "agency founder", "managing partner", "studio owner", "i own an agency", "my agency", "our agency"],
    "Delivery Manager":["delivery manager", "client delivery lead", "client services lead", "service delivery manager"],
    "Practice Lead":   ["practice director", "practice lead", "service line lead", "capability lead", "principal consultant"],
}

_PAIN_POINT_KEYWORDS: dict[str, list[str]] = {
    "Resource Utilization": [
        "utilization", "billable hours", "bench time", "resource management",
        "understaffed", "overstaffed", "over-staffed", "headcount",
        "who's available", "capacity issue",
    ],
    "Project Profitability": [
        "profit margin", "project margin", "losing money", "unprofitable",
        "project financials", "project accounting", "burn rate",
        "lost money on", "profitability",
    ],
    "Scope Creep":          ["scope creep", "out of scope", "budget overrun", "exceeded budget", "over budget"],
    "Forecasting Accuracy": ["resource forecasting", "revenue forecasting", "capacity planning", "demand planning", "forecasting accuracy"],
    "Real-time Visibility": ["real-time visibility", "reporting lag", "blind spots", "no visibility", "lack of visibility"],
    "Tool Fragmentation":   ["spreadsheets", "google sheets", "siloed", "disconnected tools", "multiple systems", "manual process", "duct tape"],
    "Time Tracking":        ["timesheet", "time capture", "time entry", "timesheet compliance", "logging hours"],
    "Client Reporting":     ["client visibility", "status reports", "client communication", "client portal"],
    "Team Burnout":         ["burnout", "overloaded", "overwhelmed", "overworked", "team burnout"],
    "Onboarding Complexity":["onboarding took", "implementation took", "setup time", "ramp time", "time to value"],
}

_COMPETITOR_KEYWORDS: dict[str, list[str]] = {
    "Wrike":         ["wrike"],
    "Workfront":     ["workfront", "adobe workfront"],
    "Mavenlink":     ["mavenlink"],
    "Kimble":        ["kimble"],
    "Certinia":      ["certinia", "financialforce", "financial force"],
    "monday.com":    ["monday.com"],
    "Smartsheet":    ["smartsheet"],
    "Asana":         ["asana"],
    "Jira":          ["jira"],
    "Harvest":       ["harvest"],
    "Resource Guru": ["resource guru"],
    "Polaris PSA":   ["polaris psa"],
    "Teamwork":      ["teamwork.com", "teamwork"],
    "NetSuite":      ["netsuite"],
    "Planview":      ["planview"],
    "Replicon":      ["replicon"],
    "BigTime":       ["bigtime", "big time software"],
}

# Intent stages are ordered from strongest to weakest signal.
# The tagger assigns the first (highest-priority) stage that matches.
_INTENT_STAGES: list[tuple[str, list[str]]] = [
    ("decision", [
        "we chose", "we picked", "we selected", "went with",
        "signed a contract", "just implemented", "switched to",
        "migrated to", "we use now", "went live", "just deployed",
        "we moved to", "we went live",
    ]),
    ("frustration", [
        "so frustrated", "so annoying", "hate this tool", "terrible tool",
        "useless for", "fed up with", "sick of", "ditching", "leaving",
        "canceling our", "rage quit", "absolutely awful",
    ]),
    ("consideration", [
        "evaluating", "comparing", "requesting a demo", "on a trial",
        "on our shortlist", "sent an rfp", "vendor evaluation",
        "scoring matrix", "getting quotes", "we're considering",
        "looking at options",
    ]),
    ("advocacy", [
        "highly recommend", "best decision we", "transformed our",
        "game changer for", "couldn't be happier", "love this tool",
        "works great for",
    ]),
    ("awareness", [
        "does anyone use", "looking for recommendations", "any alternatives",
        "what tools do you", "which tool do you", "any suggestions for",
        "what does everyone use",
    ]),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_text(record: dict[str, Any]) -> str:
    return " ".join(filter(None, [
        record.get("title") or "",
        record.get("body") or "",
    ])).lower()


def _match(text: str, keyword: str) -> bool:
    return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE))


def _match_any(text: str, keywords: list[str]) -> bool:
    return any(_match(text, kw) for kw in keywords)


def _match_terms(text: str, table: dict[str, list[str]]) -> list[str]:
    return [term for term, kws in table.items() if _match_any(text, kws)]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def tag(record: dict[str, Any]) -> dict[str, Any]:
    """
    Apply keyword-based tags to a normalized record dict.
    Returns the same dict with five tag fields populated:
      industries, buyer_roles, pain_points, competitors, intent_stage.
    Does not mutate the input — returns a new dict.
    """
    text = _build_text(record)
    sub = (record.get("subreddit") or "").lower()

    # --- industries ---
    industries: list[str] = _match_terms(text, _INDUSTRY_KEYWORDS)
    # Inject subreddit-based industry if not already present
    sub_industry = _SUB_INDUSTRY.get(sub)
    if sub_industry and sub_industry not in industries:
        industries.insert(0, sub_industry)

    # --- buyer roles ---
    buyer_roles: list[str] = _match_terms(text, _BUYER_ROLE_KEYWORDS)

    # --- pain points ---
    pain_points: list[str] = _match_terms(text, _PAIN_POINT_KEYWORDS)

    # --- competitors ---
    competitors: list[str] = _match_terms(text, _COMPETITOR_KEYWORDS)

    # --- intent stage (first matching wins in priority order) ---
    intent_stage: str | None = None
    for stage, keywords in _INTENT_STAGES:
        if _match_any(text, keywords):
            intent_stage = stage
            break

    return {
        **record,
        "industries":   industries,
        "buyer_roles":  buyer_roles,
        "pain_points":  pain_points,
        "competitors":  competitors,
        "intent_stage": intent_stage,
    }
