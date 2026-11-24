"""Session lookup + chat history, backed by MongoDB's chat_history collection."""
from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.database import get_database
from app.models.schemas import ChatHistoryItem, ChatHistoryResponse
from app.services import session_store

router = APIRouter()


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str) -> ChatHistoryResponse:
    if not session_store.has_session(session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown session_id.")

    settings = get_settings()
    try:
        db = get_database()
    except RuntimeError:
        return ChatHistoryResponse(session_id=session_id, messages=[])

    cursor = (
        db[settings.chat_history_collection_name]
        .find({"session_id": session_id}, {"_id": 0, "session_id": 0})
        .sort("timestamp", 1)
    )
    messages = [ChatHistoryItem(**doc) async for doc in cursor]
    return ChatHistoryResponse(session_id=session_id, messages=messages)
