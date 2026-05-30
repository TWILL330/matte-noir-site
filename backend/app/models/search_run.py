from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SearchRun(Base):
    """
    Audit log of every dashboard query.
    Useful for surfacing the most-used filters and common search patterns.
    """

    __tablename__ = "search_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Full filter params snapshot, e.g. {"q": "burnout", "intent_stage": "decision"}
    filters: Mapped[dict] = mapped_column(JSONB, default=dict)

    result_count: Mapped[int] = mapped_column(Integer)

    # Wall-clock query time in milliseconds
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
