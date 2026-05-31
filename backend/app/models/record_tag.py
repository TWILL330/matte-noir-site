from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordTag(Base):
    """
    Relational join between a RedditRecord and a Taxonomy term.
    Complements the JSONB tag arrays on RedditRecord for normalized querying.
    """

    __tablename__ = "record_tags"
    __table_args__ = (
        UniqueConstraint("record_id", "taxonomy_id", name="uq_record_tag"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reddit_records.id", ondelete="CASCADE"),
        index=True,
    )
    taxonomy_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("taxonomies.id", ondelete="RESTRICT"),
        index=True,
    )

    # Exact text snippet from title/body that triggered this tag
    matched_text: Mapped[str | None] = mapped_column(Text)

    # Rule-based confidence; 1.0 for exact keyword match, lower for fuzzy
    confidence: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    record: Mapped["RedditRecord"] = relationship(back_populates="record_tags")  # noqa: F821
    taxonomy: Mapped["Taxonomy"] = relationship(back_populates="record_tags")  # noqa: F821
