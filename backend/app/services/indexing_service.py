"""Phase 3 orchestrator — chunk schema, embed, and store in Atlas Vector Search."""
import logging

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services import embedding_service, schema_context, vector_store

logger = logging.getLogger(__name__)


async def build_and_store_schema_index(db: AsyncIOMotorDatabase, session_id: str, df: pd.DataFrame) -> int:
    """Run the full Phase 3 pipeline for a freshly-uploaded dataset.

    Returns the number of chunks indexed. Awaited inline from the upload
    endpoint for simplicity; a larger deployment would move this to a background task.
    """
    chunks = schema_context.build_schema_chunks(df)
    texts = [chunk["text"] for chunk in chunks]

    embeddings = await embedding_service.embed_texts(texts)
    await vector_store.store_schema_vectors(db, session_id, chunks, embeddings)

    logger.info("Indexed %d schema chunks for session %s", len(chunks), session_id)
    return len(chunks)
