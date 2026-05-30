from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
    icp_fit_score: Optional[float] = None
    pain_severity_score: Optional[float] = None
    purchase_intent_score: Optional[float] = None
    abm_priority_score: Optional[float] = None
    score_reasons: dict = {}

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    records: list[RedditRecordRead]


class ImportResponse(BaseModel):
    import_run_id: int
    filename: str
    total: int
    imported: int
    skipped: int
    errors: int
    status: str  # "complete" | "failed"
