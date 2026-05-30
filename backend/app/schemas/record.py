from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


class RedditRecordBase(BaseModel):
    source_id: str
    source_type: str
    subreddit: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    url: Optional[str] = None
    created_utc: Optional[datetime] = None
    reddit_score: Optional[int] = None
    num_comments: Optional[int] = None


class RedditRecordRead(RedditRecordBase):
    id: int
    imported_at: datetime

    industries: list[str] = []
    buyer_roles: list[str] = []
    pain_points: list[str] = []
    competitors: list[str] = []
    intent_stage: Optional[str] = None

    # Scores are integers 0–100
    icp_fit_score: Optional[int] = None
    pain_severity_score: Optional[int] = None
    purchase_intent_score: Optional[int] = None
    abm_priority_score: Optional[int] = None
    score_reasons: dict[str, str] = {}

    model_config = {"from_attributes": True}

    @field_validator("industries", "buyer_roles", "pain_points", "competitors", mode="before")
    @classmethod
    def coerce_list(cls, v: Any) -> list:
        return v if isinstance(v, list) else []

    @field_validator("score_reasons", mode="before")
    @classmethod
    def coerce_dict(cls, v: Any) -> dict:
        return v if isinstance(v, dict) else {}

    @field_validator(
        "icp_fit_score", "pain_severity_score",
        "purchase_intent_score", "abm_priority_score",
        mode="before",
    )
    @classmethod
    def coerce_score(cls, v: Any) -> Optional[int]:
        if v is None:
            return None
        return int(round(float(v)))


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    records: list[RedditRecordRead]


class FacetsResponse(BaseModel):
    industries: list[str]
    buyer_roles: list[str]
    pain_points: list[str]
    competitors: list[str]
    intent_stages: list[str]
    subreddits: list[str]


class ImportResponse(BaseModel):
    import_run_id: int
    filename: str
    total: int
    imported: int
    skipped: int
    errors: int
    status: str  # "complete" | "failed"
