"""
Controlled vocabulary for all five tagging dimensions.
Mirrors the keyword lists used by the tagger so the taxonomy table
stays in sync with what the enrichment pipeline actually detects.
"""

TAXONOMY: dict[str, list[dict]] = {
    "industry": [
        {
            "term": "Marketing Agency",
            "aliases": [
                "ad agency", "creative agency", "digital agency",
                "advertising agency", "media agency", "branding agency",
            ],
        },
        {
            "term": "IT Services",
            "aliases": [
                "managed services", "msp", "it consulting", "systems integrator",
                "it services", "technology services", "tech consulting",
            ],
        },
        {
            "term": "Management Consulting",
            "aliases": [
                "consulting firm", "management consulting", "strategy consulting",
                "consultancy", "professional services", "advisory firm",
            ],
        },
        {
            "term": "Architecture Engineering Construction",
            "aliases": [
                "aec", "architecture firm", "engineering firm", "construction firm",
                "design firm", "structural engineering", "civil engineering",
            ],
        },
        {
            "term": "Legal Services",
            "aliases": [
                "law firm", "legal practice", "attorneys", "litigation",
                "legal services", "solicitors", "legal advisory",
            ],
        },
        {
            "term": "Accounting & Finance",
            "aliases": [
                "cpa firm", "accounting firm", "financial advisory", "audit firm",
                "tax firm", "bookkeeping", "financial services",
            ],
        },
        {
            "term": "Software & Technology Services",
            "aliases": [
                "software development", "saas company", "tech startup",
                "development shop", "software consulting", "dev shop",
            ],
        },
        {
            "term": "Staffing & Recruiting",
            "aliases": [
                "staffing agency", "recruiting firm", "talent agency",
                "headhunting", "workforce solutions",
            ],
        },
        {
            "term": "PR & Communications",
            "aliases": [
                "public relations", "pr firm", "communications agency",
                "media relations", "corporate communications",
            ],
        },
        {
            "term": "Research & Analytics",
            "aliases": [
                "market research", "data analytics", "insights firm",
                "research firm", "analytics consulting",
            ],
        },
    ],

    "buyer_role": [
        {
            "term": "PMO Director",
            "aliases": [
                "head of pmo", "director of project management",
                "vp of pmo", "pmo lead", "pmo manager",
            ],
        },
        {
            "term": "VP of Operations",
            "aliases": [
                "coo", "chief operating officer", "vp of operations",
                "operations director", "vp ops", "director of operations",
            ],
        },
        {
            "term": "Project Manager",
            "aliases": [
                "project manager", "engagement manager", "delivery manager",
                "project lead", "project management", "program manager",
            ],
        },
        {
            "term": "Resource Manager",
            "aliases": [
                "resource manager", "resource planner", "capacity planner",
                "staffing manager", "workforce manager", "resource management",
            ],
        },
        {
            "term": "Finance Director",
            "aliases": [
                "cfo", "chief financial officer", "finance director",
                "financial controller", "vp of finance", "director of finance",
            ],
        },
        {
            "term": "IT Manager",
            "aliases": [
                "it manager", "it director", "cto", "vp of it",
                "technology manager", "tech lead", "director of it",
            ],
        },
        {
            "term": "Agency Owner",
            "aliases": [
                "agency owner", "agency founder", "managing partner",
                "studio owner", "i own", "my agency", "our agency",
            ],
        },
        {
            "term": "Delivery Manager",
            "aliases": [
                "delivery manager", "client delivery lead", "client services lead",
                "portfolio manager", "service delivery",
            ],
        },
        {
            "term": "Practice Lead",
            "aliases": [
                "practice director", "practice lead", "service line lead",
                "capability lead", "principal consultant",
            ],
        },
    ],

    "pain_point": [
        {
            "term": "Resource Utilization",
            "aliases": [
                "utilization", "billable hours", "bench time", "capacity",
                "understaffed", "overstaffed", "over-staffed",
                "resource management", "headcount", "who's available",
            ],
        },
        {
            "term": "Project Profitability",
            "aliases": [
                "margin", "profit margin", "losing money", "unprofitable",
                "project financials", "project accounting", "burn rate",
                "lost money", "profitability",
            ],
        },
        {
            "term": "Scope Creep",
            "aliases": [
                "scope creep", "out of scope", "budget overrun",
                "exceeded budget", "over budget", "feature creep",
            ],
        },
        {
            "term": "Forecasting Accuracy",
            "aliases": [
                "forecasting", "forecast", "pipeline visibility",
                "revenue forecast", "capacity planning", "resource forecasting",
                "demand planning", "no forecast",
            ],
        },
        {
            "term": "Real-time Visibility",
            "aliases": [
                "real-time", "visibility", "reporting lag", "blind spots",
                "no visibility", "can't see", "don't know", "lack of visibility",
            ],
        },
        {
            "term": "Tool Fragmentation",
            "aliases": [
                "spreadsheet", "excel", "siloed", "disconnected tools",
                "multiple systems", "manual process", "duct tape",
                "workaround", "copy paste",
            ],
        },
        {
            "term": "Time Tracking",
            "aliases": [
                "timesheet", "time capture", "time entry",
                "timesheet compliance", "logging hours", "timekeeping",
            ],
        },
        {
            "term": "Client Reporting",
            "aliases": [
                "client visibility", "status report", "client communication",
                "project status", "client dashboard", "client portal",
            ],
        },
        {
            "term": "Team Burnout",
            "aliases": [
                "burnout", "overloaded", "overwhelmed", "overworked",
                "overtime", "stress", "too much work", "exhausted",
            ],
        },
        {
            "term": "Onboarding Complexity",
            "aliases": [
                "implementation", "onboarding took", "configuration",
                "setup time", "ramp time", "time to value",
            ],
        },
    ],

    "competitor": [
        {"term": "Wrike",         "aliases": ["wrike"]},
        {"term": "Workfront",     "aliases": ["workfront", "adobe workfront"]},
        {"term": "Mavenlink",     "aliases": ["mavenlink"]},
        {"term": "Kimble",        "aliases": ["kimble", "kimble psa"]},
        {"term": "Certinia",      "aliases": ["certinia", "financialforce", "financial force"]},
        {"term": "monday.com",    "aliases": ["monday.com"]},
        {"term": "Smartsheet",    "aliases": ["smartsheet"]},
        {"term": "Asana",         "aliases": ["asana"]},
        {"term": "Jira",          "aliases": ["jira"]},
        {"term": "Harvest",       "aliases": ["harvest", "getharvest"]},
        {"term": "Resource Guru", "aliases": ["resource guru"]},
        {"term": "Polaris PSA",   "aliases": ["polaris psa", "polaris"]},
        {"term": "Teamwork",      "aliases": ["teamwork.com", "teamwork"]},
        {"term": "NetSuite",      "aliases": ["netsuite"]},
        {"term": "Planview",      "aliases": ["planview"]},
        {"term": "Replicon",      "aliases": ["replicon"]},
        {"term": "BigTime",       "aliases": ["bigtime", "big time software"]},
    ],

    "intent_stage": [
        {
            "term": "awareness",
            "aliases": [
                "what is", "looking for options", "any recommendations",
                "does anyone use", "alternatives to", "what tools",
                "which tools", "any suggestions", "what do you use",
            ],
        },
        {
            "term": "consideration",
            "aliases": [
                "evaluating", "comparing", "demo", "trial", "shortlist",
                "rfp", "vendor evaluation", "scoring matrix", "pricing",
                "considering", "we're looking", "anyone used",
            ],
        },
        {
            "term": "decision",
            "aliases": [
                "we chose", "we picked", "we selected", "went with",
                "signed contract", "just implemented", "switched to",
                "migrated to", "we use now", "went live", "just deployed",
            ],
        },
        {
            "term": "frustration",
            "aliases": [
                "hate", "terrible", "frustrating", "annoying", "broken",
                "useless", "ditching", "leaving", "canceling", "fed up",
                "sick of", "awful", "worst", "rage quit",
            ],
        },
        {
            "term": "advocacy",
            "aliases": [
                "love", "highly recommend", "great tool", "best decision",
                "transformed", "game changer", "works great", "fantastic",
                "couldn't be happier", "five stars",
            ],
        },
    ],
}
