from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Valid taxonomy categories — mirrors the five tag dimensions on RedditRecord
TAXONOMY_CATEGORIES = frozenset(
    {"industry", "buyer_role", "pain_point", "competitor", "intent_stage"}
)


class Taxonomy(Base):
    """
    Controlled vocabulary for all tagging dimensions.
    The tagger service matches text against these terms and their aliases.
    """

    __tablename__ = "taxonomies"
    __table_args__ = (
        UniqueConstraint("category", "term", name="uq_taxonomy_category_term"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # e.g. "industry" | "buyer_role" | "pain_point" | "competitor" | "intent_stage"
    category: Mapped[str] = mapped_column(String(64), index=True)

    # Display-ready canonical label, e.g. "Marketing Agency"
    term: Mapped[str] = mapped_column(String(128))

    # Alternate spellings / abbreviations the tagger uses for matching
    aliases: Mapped[list | None] = mapped_column(JSONB, default=list)

    # Soft-delete without breaking historical record_tags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    record_tags: Mapped[list["RecordTag"]] = relationship(  # noqa: F821
        back_populates="taxonomy"
    )
