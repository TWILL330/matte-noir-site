from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExportLog(Base):
    """
    Audit log of every CSV export.
    Captures the filter state so exports can be reproduced.
    """

    __tablename__ = "export_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Filter params active at export time
    filters: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Number of rows written to the CSV
    row_count: Mapped[int] = mapped_column(Integer)

    # Auto-generated filename sent to the browser
    filename: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
