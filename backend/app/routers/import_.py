from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.import_run import ImportRun
from app.models.record import RedditRecord
from app.providers.manual_import import ManualImportProvider
from app.schemas.record import ImportResponse
from app.services.normalizer import normalize

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
    Records are normalized and persisted; duplicates by source_id are skipped.
    """
    # --- validate extension ---
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload a .csv or .json file.",
        )

    # --- read content ---
    content = await file.read()
    if len(content) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit.")
    if not content.strip():
        raise HTTPException(status_code=400, detail="File is empty.")

    # --- create ImportRun audit record ---
    run = ImportRun(
        filename=filename,
        file_format=ext.lstrip("."),
        status="pending",
    )
    db.add(run)
    db.flush()  # populate run.id before we reference it on records

    # --- parse ---
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

    # --- load existing source_ids once to avoid per-row queries ---
    # Acceptable for MVP scale; revisit with a bloom filter if rows > 1M
    existing: set[str] = {
        row[0] for row in db.query(RedditRecord.source_id).all()
    }

    imported = skipped = errors = 0
    to_add: list[RedditRecord] = []

    for raw in raw_rows:
        # normalize
        try:
            normalized = normalize(raw)
        except Exception:
            errors += 1
            continue

        if normalized is None:
            # row had no usable text content
            errors += 1
            continue

        # deduplication
        sid = normalized["source_id"]
        if sid in existing:
            skipped += 1
            continue

        existing.add(sid)  # guard against duplicates within the same upload
        to_add.append(RedditRecord(**normalized, import_run_id=run.id))
        imported += 1

    # --- persist ---
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
        raise HTTPException(
            status_code=500,
            detail=f"Database error while saving records: {exc}",
        )

    return ImportResponse(
        import_run_id=run.id,
        filename=run.filename,
        total=run.total_rows,
        imported=imported,
        skipped=skipped,
        errors=errors,
        status=run.status,
    )
