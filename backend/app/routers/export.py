import csv
import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.export_log import ExportLog
from app.models.record import RedditRecord
from app.routers.records import _build_query

router = APIRouter()

_COLUMNS = [
    "id", "source_id", "source_type", "subreddit", "author",
    "title", "body_preview", "url", "created_utc", "imported_at",
    "reddit_score", "num_comments",
    "industries", "buyer_roles", "pain_points", "competitors", "intent_stage",
    "icp_fit_score", "pain_severity_score", "purchase_intent_score", "abm_priority_score",
]


def _row(r: RedditRecord) -> dict:
    def join(v) -> str:
        return " | ".join(v) if v else ""

    return {
        "id":                   r.id,
        "source_id":            r.source_id,
        "source_type":          r.source_type,
        "subreddit":            r.subreddit or "",
        "author":               r.author or "",
        "title":                r.title or "",
        "body_preview":         (r.body or "")[:300].replace("\n", " "),
        "url":                  r.url or "",
        "created_utc":          r.created_utc.isoformat() if r.created_utc else "",
        "imported_at":          r.imported_at.isoformat(),
        "reddit_score":         r.reddit_score if r.reddit_score is not None else "",
        "num_comments":         r.num_comments if r.num_comments is not None else "",
        "industries":           join(r.industries),
        "buyer_roles":          join(r.buyer_roles),
        "pain_points":          join(r.pain_points),
        "competitors":          join(r.competitors),
        "intent_stage":         r.intent_stage or "",
        "icp_fit_score":        r.icp_fit_score if r.icp_fit_score is not None else "",
        "pain_severity_score":  r.pain_severity_score if r.pain_severity_score is not None else "",
        "purchase_intent_score":r.purchase_intent_score if r.purchase_intent_score is not None else "",
        "abm_priority_score":   r.abm_priority_score if r.abm_priority_score is not None else "",
    }


@router.get("")
def export_csv(
    q: Optional[str] = None,
    subreddit: Optional[str] = None,
    industry: Optional[str] = None,
    buyer_role: Optional[str] = None,
    pain_point: Optional[str] = None,
    competitor: Optional[str] = None,
    intent_stage: Optional[str] = None,
    min_icp_fit: Optional[int] = None,
    min_pain_severity: Optional[int] = None,
    min_purchase_intent: Optional[int] = None,
    min_abm_priority: Optional[int] = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Export filtered records to CSV. Same filter params as GET /records."""
    query = _build_query(
        db, q, subreddit, industry, buyer_role, pain_point,
        competitor, intent_stage, min_icp_fit, min_pain_severity,
        min_purchase_intent, min_abm_priority,
    )
    records = (
        query
        .order_by(RedditRecord.abm_priority_score.desc().nullslast())
        .all()
    )

    # Build CSV in memory (internal tool; datasets fit easily in RAM)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for r in records:
        writer.writerow(_row(r))

    # Log the export
    try:
        filename = f"kantata_intel_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        db.add(ExportLog(
            filters={k: v for k, v in {
                "q": q, "subreddit": subreddit, "industry": industry,
                "buyer_role": buyer_role, "pain_point": pain_point,
                "competitor": competitor, "intent_stage": intent_stage,
                "min_icp_fit": min_icp_fit, "min_abm_priority": min_abm_priority,
            }.items() if v is not None},
            row_count=len(records),
            filename=filename,
        ))
        db.commit()
    except Exception:
        pass  # don't fail the export if logging fails

    output.seek(0)
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
