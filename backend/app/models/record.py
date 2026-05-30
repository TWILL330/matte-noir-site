from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RedditRecord(Base):
    __tablename__ = "reddit_records"
    __table_args__ = (
        # Composite indexes for the most common dashboard filter combinations
        Index("ix_records_intent_abm", "intent_stage", "abm_priority_score"),
        Index("ix_records_imported_at", "imported_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # FK to the batch that brought this record in
    import_run_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("import_runs.id", ondelete="SET NULL"),
        index=True,
    )

    # Source fields
    source_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(32))  # "post" | "comment"
    subreddit: Mapped[str | None] = mapped_column(String(128), index=True)
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

    # Denormalized tags — populated by tagger service for fast JSONB filtering
    industries: Mapped[list | None] = mapped_column(JSONB, default=list)
    buyer_roles: Mapped[list | None] = mapped_column(JSONB, default=list)
    pain_points: Mapped[list | None] = mapped_column(JSONB, default=list)
    competitors: Mapped[list | None] = mapped_column(JSONB, default=list)
    intent_stage: Mapped[str | None] = mapped_column(String(64), index=True)

    # Denormalized scores — source of truth for dashboard filtering (0.0–1.0)
    icp_fit_score: Mapped[float | None] = mapped_column(Float, index=True)
    pain_severity_score: Mapped[float | None] = mapped_column(Float)
    purchase_intent_score: Mapped[float | None] = mapped_column(Float, index=True)
    abm_priority_score: Mapped[float | None] = mapped_column(Float, index=True)

    # Compact score explanation for the detail view (full reasons live in Score)
    score_reasons: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Relationships
    import_run: Mapped["ImportRun | None"] = relationship(  # noqa: F821
        back_populates="records"
    )
    record_tags: Mapped[list["RecordTag"]] = relationship(  # noqa: F821
        back_populates="record", cascade="all, delete-orphan"
    )
    score: Mapped["Score | None"] = relationship(  # noqa: F821
        back_populates="record", cascade="all, delete-orphan", uselist=False
    )
