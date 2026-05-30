from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.record import RedditRecord
from app.models.taxonomy import Taxonomy
from app.schemas.record import FacetsResponse, RecordListResponse, RedditRecordRead

router = APIRouter()


def _build_query(
    db: Session,
    q: Optional[str],
    subreddit: Optional[str],
    industry: Optional[str],
    buyer_role: Optional[str],
    pain_point: Optional[str],
    competitor: Optional[str],
    intent_stage: Optional[str],
    min_icp_fit: Optional[int],
    min_pain_severity: Optional[int],
    min_purchase_intent: Optional[int],
    min_abm_priority: Optional[int],
):
    """Shared filter builder used by both list and export."""
    query = db.query(RedditRecord)

    if q:
        term = f"%{q}%"
        from sqlalchemy import or_
        query = query.filter(
            or_(
                RedditRecord.title.ilike(term),
                RedditRecord.body.ilike(term),
            )
        )

    if subreddit:
        query = query.filter(func.lower(RedditRecord.subreddit) == subreddit.lower())

    if industry:
        query = query.filter(RedditRecord.industries.contains([industry]))

    if buyer_role:
        query = query.filter(RedditRecord.buyer_roles.contains([buyer_role]))

    if pain_point:
        query = query.filter(RedditRecord.pain_points.contains([pain_point]))

    if competitor:
        query = query.filter(RedditRecord.competitors.contains([competitor]))

    if intent_stage:
        query = query.filter(RedditRecord.intent_stage == intent_stage)

    if min_icp_fit is not None:
        query = query.filter(RedditRecord.icp_fit_score >= min_icp_fit)

    if min_pain_severity is not None:
        query = query.filter(RedditRecord.pain_severity_score >= min_pain_severity)

    if min_purchase_intent is not None:
        query = query.filter(RedditRecord.purchase_intent_score >= min_purchase_intent)

    if min_abm_priority is not None:
        query = query.filter(RedditRecord.abm_priority_score >= min_abm_priority)

    return query


# IMPORTANT: /facets must be declared before /{record_id} so FastAPI
# matches the literal path before trying to cast "facets" to int.
@router.get("/facets", response_model=FacetsResponse)
def get_facets(db: Session = Depends(get_db)) -> FacetsResponse:
    """Return available filter options for the dashboard dropdowns."""

    def taxonomy_terms(category: str) -> list[str]:
        return [
            t.term
            for t in db.query(Taxonomy)
            .filter_by(category=category, is_active=True)
            .order_by(Taxonomy.term)
            .all()
        ]

    subreddits = [
        row[0]
        for row in db.query(distinct(RedditRecord.subreddit))
        .filter(RedditRecord.subreddit.isnot(None))
        .order_by(RedditRecord.subreddit)
        .all()
    ]

    intent_stages = [
        row[0]
        for row in db.query(distinct(RedditRecord.intent_stage))
        .filter(RedditRecord.intent_stage.isnot(None))
        .order_by(RedditRecord.intent_stage)
        .all()
    ]

    return FacetsResponse(
        industries=taxonomy_terms("industry"),
        buyer_roles=taxonomy_terms("buyer_role"),
        pain_points=taxonomy_terms("pain_point"),
        competitors=taxonomy_terms("competitor"),
        intent_stages=intent_stages,
        subreddits=subreddits,
    )


@router.get("", response_model=RecordListResponse)
def list_records(
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
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> RecordListResponse:
    page = max(1, page)
    page_size = max(1, min(100, page_size))

    query = _build_query(
        db, q, subreddit, industry, buyer_role, pain_point,
        competitor, intent_stage, min_icp_fit, min_pain_severity,
        min_purchase_intent, min_abm_priority,
    )

    total = query.count()
    records = (
        query
        .order_by(RedditRecord.abm_priority_score.desc().nullslast())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        records=[RedditRecordRead.model_validate(r) for r in records],
    )


@router.get("/{record_id}", response_model=RedditRecordRead)
def get_record(record_id: int, db: Session = Depends(get_db)) -> RedditRecordRead:
    record = db.query(RedditRecord).filter(RedditRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    return RedditRecordRead.model_validate(record)
