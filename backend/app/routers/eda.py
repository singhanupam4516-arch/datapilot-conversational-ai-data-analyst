"""Phase 2 endpoint — computes and returns EDA for an uploaded session."""
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import EDAResponse
from app.services import eda_engine, session_store

router = APIRouter()


@router.get("/eda/{session_id}", response_model=EDAResponse)
async def get_eda(session_id: str) -> EDAResponse:
    df = session_store.get_dataframe(session_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown session_id — upload a spreadsheet first.",
        )
    return EDAResponse(**eda_engine.run_eda(df))
