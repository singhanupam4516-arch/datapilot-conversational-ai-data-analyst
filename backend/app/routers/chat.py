"""Phase 4 endpoint — the conversational loop.

Question -> embed -> Atlas Vector Search retrieval -> LLM writes Pandas code
-> code is sandbox-validated and executed -> result is phrased back in
natural language -> the whole interaction is saved to chat_history.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.database import get_database
from app.models.schemas import ChatRequest, ChatResponse
from app.services import code_executor, embedding_service, llm_service, session_store, vector_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat/{session_id}", response_model=ChatResponse)
async def chat_with_data(session_id: str, chat_request: ChatRequest) -> ChatResponse:
    df = session_store.get_dataframe(session_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown session_id — upload a spreadsheet first.",
        )

    settings = get_settings()
    question = chat_request.message.strip()

    try:
        db = get_database()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    try:
        query_embedding = await embedding_service.embed_query(question)
        context_chunks = await vector_store.retrieve_relevant_context(db, session_id, query_embedding)
        context = "\n".join(context_chunks) if context_chunks else "No indexed schema context is available yet."

        generated_code = await llm_service.generate_pandas_code(question, context)
        execution = code_executor.execute_pandas_code(generated_code, df)
        answer_text = await llm_service.phrase_answer(question, execution["result"])
    except code_executor.CodeSafetyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Blocked unsafe generated code: {exc}",
        ) from exc
    except code_executor.CodeExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Generated code failed to run: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Chat pipeline failed for session %s", session_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"The AI pipeline failed: {exc}",
        ) from exc

    timestamp = datetime.now(timezone.utc)
    chat_document = {
        "session_id": session_id,
        "question": question,
        "answer": answer_text,
        "generated_code": generated_code,
        "result": execution["result"],
        "chart_base64": execution["chart_base64"],
        "timestamp": timestamp,
    }
    await db[settings.chat_history_collection_name].insert_one(dict(chat_document))

    return ChatResponse(
        answer=answer_text,
        generated_code=generated_code,
        result=execution["result"],
        chart_base64=execution["chart_base64"],
        timestamp=timestamp,
    )
