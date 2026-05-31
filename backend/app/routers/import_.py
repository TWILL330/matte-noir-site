from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.import_run import ImportRun
from app.models.record import RedditRecord
from app.models.score import Score
from app.providers.manual_import import ManualImportProvider
from app.schemas.record import ImportResponse
from app.services.normalizer import normalize
from app.services.tagger import tag
from app.services.scorer import score

router = APIRouter()

_ALLOWED = {".csv", ".json"}
_MAX_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("", response_model=ImportResponse)
async def import_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImportResponse:
    """
    Upload a CSV or JSON file of Reddit posts/comments.
    Each row is normalized → tagged → scored → persisted.
    Duplicates (by source_id) are skipped.
    """
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()

    if ext not in _ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload a .csv or .json file.",
        )

    content = await file.read()
    if len(content) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit.")
    if not content.strip():
        raise HTTPException(status_code=400, detail="File is empty.")

    # Create audit record before touching any rows
    run = ImportRun(filename=filename, file_format=ext.lstrip("."), status="pending")
    db.add(run)
    db.flush()

    # Parse
    try:
        raw_rows = (
            ManualImportProvider.from_csv(content)
            if ext == ".csv"
            else ManualImportProvider.from_json(content)
        )
    except Exception as exc:
        run.status = "failed"
        run.error_detail = str(exc)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}")

    run.total_rows = len(raw_rows)

    # Load existing source_ids once for O(1) deduplication
    existing: set[str] = {row[0] for row in db.query(RedditRecord.source_id).all()}

    imported = skipped = errors = 0
    to_add: list[RedditRecord] = []

    for raw in raw_rows:
        # Normalize
        try:
            normalized = normalize(raw)
        except Exception:
            errors += 1
            continue

        if normalized is None:
            errors += 1
            continue

        # Deduplicate
        sid = normalized["source_id"]
        if sid in existing:
            skipped += 1
            continue
        existing.add(sid)

        # Enrich
        try:
            tagged = tag(normalized)
            scored = score(tagged)
        except Exception:
            errors += 1
            continue

        # Build ORM objects
        record = RedditRecord(
            import_run_id=run.id,
            source_id=normalized["source_id"],
            source_type=normalized["source_type"],
            subreddit=normalized["subreddit"],
            author=normalized["author"],
            title=normalized["title"],
            body=normalized["body"],
            url=normalized["url"],
            created_utc=normalized["created_utc"],
            reddit_score=normalized["reddit_score"],
            num_comments=normalized["num_comments"],
            industries=tagged["industries"],
            buyer_roles=tagged["buyer_roles"],
            pain_points=tagged["pain_points"],
            competitors=tagged["competitors"],
            intent_stage=tagged["intent_stage"],
            icp_fit_score=scored["icp_fit_score"],
            pain_severity_score=scored["pain_severity_score"],
            purchase_intent_score=scored["purchase_intent_score"],
            abm_priority_score=scored["abm_priority_score"],
            score_reasons=scored["score_reasons"],
        )
        # Score detail cascades via relationship
        record.score = Score(
            icp_fit_score=scored["icp_fit_score"],
            pain_severity_score=scored["pain_severity_score"],
            purchase_intent_score=scored["purchase_intent_score"],
            abm_priority_score=scored["abm_priority_score"],
            icp_fit_reasons=scored["icp_fit_reasons"],
            pain_severity_reasons=scored["pain_severity_reasons"],
            purchase_intent_reasons=scored["purchase_intent_reasons"],
            abm_priority_reasons=scored["abm_priority_reasons"],
            score_version="v1",
        )
        to_add.append(record)
        imported += 1

    # Persist
    try:
        db.add_all(to_add)
        run.imported_count = imported
        run.skipped_count = skipped
        run.error_count = errors
        run.status = "complete"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        run.status = "failed"
        run.error_detail = str(exc)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    return ImportResponse(
        import_run_id=run.id,
        filename=run.filename,
        total=run.total_rows,
        imported=imported,
        skipped=skipped,
        errors=errors,
        status=run.status,
    )
