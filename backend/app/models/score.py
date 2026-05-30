from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Score(Base):
    """
    Detailed score breakdown for a RedditRecord.

    The summary floats (icp_fit_score etc.) are denormalized onto RedditRecord
    for fast dashboard filtering. This table stores the per-dimension reasoning
    lists that explain how each score was reached.
    """

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reddit_records.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Mirrors the summary floats on RedditRecord (source of truth for queries)
    icp_fit_score: Mapped[float | None] = mapped_column(Float)
    pain_severity_score: Mapped[float | None] = mapped_column(Float)
    purchase_intent_score: Mapped[float | None] = mapped_column(Float)
    abm_priority_score: Mapped[float | None] = mapped_column(Float)

    # Per-dimension reason lists, e.g. ["+0.3: matched 'agency' in industry list"]
    icp_fit_reasons: Mapped[list | None] = mapped_column(JSONB, default=list)
    pain_severity_reasons: Mapped[list | None] = mapped_column(JSONB, default=list)
    purchase_intent_reasons: Mapped[list | None] = mapped_column(JSONB, default=list)
    abm_priority_reasons: Mapped[list | None] = mapped_column(JSONB, default=list)

    # Bump this string when scoring rules change so stale scores can be re-run
    score_version: Mapped[str] = mapped_column(String(32), default="v1", index=True)

    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    record: Mapped["RedditRecord"] = relationship(back_populates="score")  # noqa: F821
