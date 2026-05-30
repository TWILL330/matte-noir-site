from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RedditRecord(Base):
    __tablename__ = "reddit_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Source fields
    source_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(32))  # "post" | "comment"
    subreddit: Mapped[str | None] = mapped_column(String(128))
    author: Mapped[str | None] = mapped_column(String(128))
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    created_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reddit_score: Mapped[int | None] = mapped_column(Integer)
    num_comments: Mapped[int | None] = mapped_column(Integer)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Tags — populated by tagger service
    industries: Mapped[list | None] = mapped_column(JSONB, default=list)
    buyer_roles: Mapped[list | None] = mapped_column(JSONB, default=list)
    pain_points: Mapped[list | None] = mapped_column(JSONB, default=list)
    competitors: Mapped[list | None] = mapped_column(JSONB, default=list)
    intent_stage: Mapped[str | None] = mapped_column(String(64))

    # Scores — populated by scorer service (0.0–1.0)
    icp_fit_score: Mapped[float | None] = mapped_column(Float)
    pain_severity_score: Mapped[float | None] = mapped_column(Float)
    purchase_intent_score: Mapped[float | None] = mapped_column(Float)
    abm_priority_score: Mapped[float | None] = mapped_column(Float)

    # Human-readable explanation of how scores were derived
    score_reasons: Mapped[dict | None] = mapped_column(JSONB, default=dict)
