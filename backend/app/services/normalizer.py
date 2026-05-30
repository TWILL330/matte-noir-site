import hashlib
from datetime import datetime, timezone
from typing import Any

# Priority-ordered aliases for each canonical RedditRecord field.
# First match wins when scanning a raw provider row.
_ALIASES: dict[str, list[str]] = {
    "source_id":    ["source_id", "id", "name", "post_id", "comment_id"],
    "source_type":  ["source_type", "type", "kind"],
    "subreddit":    ["subreddit", "subreddit_name_prefixed", "subreddit_name"],
    "author":       ["author", "username", "user"],
    "title":        ["title"],
    "body":         ["body", "selftext", "text", "content"],
    "url":          ["url", "full_link", "permalink", "link"],
    "created_utc":  ["created_utc", "created", "timestamp", "date", "created_at"],
    "reddit_score": ["score", "reddit_score", "upvotes", "ups"],
    "num_comments": ["num_comments", "comment_count", "comments"],
}

# Values that should be treated as absent
_EMPTY = {"", "none", "null", "[deleted]", "[removed]"}


def _pick(raw: dict, aliases: list[str]) -> Any:
    """Return the first non-empty value found under any alias key."""
    for key in aliases:
        v = raw.get(key)
        if v is not None and str(v).strip().lower() not in _EMPTY:
            return v
    return None


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    # Unix timestamp (int or float-as-string)
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        pass
    # ISO 8601 string
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_int(value: Any) -> int | None:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def _clean_subreddit(value: Any) -> str | None:
    if not value:
        return None
    return str(value).strip().lstrip("r/").strip() or None


def _infer_source_type(raw: dict, title: str | None) -> str:
    raw_type = _pick(raw, _ALIASES["source_type"])
    if raw_type:
        t = str(raw_type).lower()
        if "comment" in t:
            return "comment"
        if "post" in t or "link" in t or "submission" in t:
            return "post"
    # Fall back to structural inference: posts have titles
    return "post" if title else "comment"


def _stable_id(raw: dict) -> str:
    """Deterministic fallback source_id derived from row content."""
    key = "|".join(f"{k}={raw[k]}" for k in sorted(raw) if raw[k])
    return "gen_" + hashlib.sha1(key.encode()).hexdigest()[:16]


def normalize(raw: dict[str, Any]) -> dict[str, Any] | None:
    """
    Map a raw provider row to the RedditRecord field set.

    Returns None when the row has no usable text content (no title and no body),
    which the caller should count as an error/skip.
    """
    title_raw = _pick(raw, _ALIASES["title"])
    body_raw = _pick(raw, _ALIASES["body"])

    title = str(title_raw).strip() if title_raw else None
    body = str(body_raw).strip() if body_raw else None

    if not title and not body:
        return None

    source_id_raw = _pick(raw, _ALIASES["source_id"])
    source_id = str(source_id_raw).strip() if source_id_raw else _stable_id(raw)

    return {
        "source_id":             source_id,
        "source_type":           _infer_source_type(raw, title),
        "subreddit":             _clean_subreddit(_pick(raw, _ALIASES["subreddit"])),
        "author":                str(_pick(raw, _ALIASES["author"]) or "").strip() or None,
        "title":                 title,
        "body":                  body,
        "url":                   str(_pick(raw, _ALIASES["url"]) or "").strip() or None,
        "created_utc":           _parse_dt(_pick(raw, _ALIASES["created_utc"])),
        "reddit_score":          _parse_int(_pick(raw, _ALIASES["reddit_score"])),
        "num_comments":          _parse_int(_pick(raw, _ALIASES["num_comments"])),
        # Tags and scores are populated later by the tagger / scorer services
        "industries":            [],
        "buyer_roles":           [],
        "pain_points":           [],
        "competitors":           [],
        "intent_stage":          None,
        "icp_fit_score":         None,
        "pain_severity_score":   None,
        "purchase_intent_score": None,
        "abm_priority_score":    None,
        "score_reasons":         {},
    }
