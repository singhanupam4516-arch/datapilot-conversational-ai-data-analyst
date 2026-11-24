"""Phase 1 endpoint — receives a spreadsheet, cleans it, indexes it, and
persists upload metadata to MongoDB Atlas."""
import logging
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.database import get_database
from app.models.schemas import ColumnInfo, UploadResponse
from app.services import data_ingestion, indexing_service, session_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_spreadsheet(file: UploadFile = File(...)) -> UploadResponse:
    settings = get_settings()
    file_bytes = await file.read()

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_size_mb}MB limit.",
        )

    try:
        raw_df = data_ingestion.load_dataframe(file.filename or "upload.csv", file_bytes)
    except data_ingestion.UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    cleaned_df = data_ingestion.clean_dataframe(raw_df)

    session_id = str(uuid.uuid4())
    session_store.save_dataframe(session_id, cleaned_df)

    summary = data_ingestion.build_upload_summary(cleaned_df, file.filename or "upload.csv", session_id)

    try:
        db = get_database()
        await db[settings.uploads_collection_name].insert_one(dict(summary))
    except RuntimeError as exc:
        logger.warning("Skipped persisting upload metadata (DB unavailable): %s", exc)
    else:
        try:
            await indexing_service.build_and_store_schema_index(db, session_id, cleaned_df)
        except Exception as exc:
            # Indexing calls an external embedding API — don't fail the whole
            # upload if it's unreachable. The dashboard still works; chat will
            # surface a clear error until indexing succeeds.
            logger.warning("Schema indexing failed for session %s: %s", session_id, exc)

    return UploadResponse(
        session_id=session_id,
        filename=summary["filename"],
        row_count=summary["row_count"],
        column_count=summary["column_count"],
        columns=[ColumnInfo(name=c["name"], dtype=c["dtype"]) for c in summary["columns"]],
        uploaded_at=summary["uploaded_at"],
    )
