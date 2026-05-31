from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ImportRun(Base):
    """
    Audit record for a single file import operation.
    Each batch of records uploaded together shares one ImportRun.
    """

    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_format: Mapped[str] = mapped_column(String(16))  # "csv" | "json"

    # Row counts set after processing completes
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    imported_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)  # duplicates
    error_count: Mapped[int] = mapped_column(Integer, default=0)

    # "pending" → "complete" | "failed"
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    error_detail: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    records: Mapped[list["RedditRecord"]] = relationship(  # noqa: F821
        back_populates="import_run"
    )
