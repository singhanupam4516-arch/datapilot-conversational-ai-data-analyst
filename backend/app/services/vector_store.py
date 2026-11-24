"""Phase 3 (storage) & Phase 4 (retrieval) — MongoDB Atlas Vector Search.

The `$vectorSearch` query is issued directly through Motor (async) rather than
LangChain's synchronous MongoDBAtlasVectorSearch wrapper, keeping the whole
FastAPI request path non-blocking.
"""
import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings

logger = logging.getLogger(__name__)


async def store_schema_vectors(
    db: AsyncIOMotorDatabase,
    session_id: str,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    """Persist embedded schema chunks for a session (Phase 3)."""
    settings = get_settings()
    collection = db[settings.vector_collection_name]

    # Replace any previous vectors for this session (e.g. the user re-uploads).
    await collection.delete_many({"session_id": session_id})

    documents = [
        {
            "session_id": session_id,
            "chunk_type": chunk["chunk_type"],
            "column_name": chunk["column_name"],
            "text": chunk["text"],
            "embedding": embedding,
            "created_at": datetime.now(timezone.utc),
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]
    if documents:
        await collection.insert_many(documents)


async def retrieve_relevant_context(
    db: AsyncIOMotorDatabase,
    session_id: str,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[str]:
    """Run Atlas Vector Search scoped to this session's own schema chunks.

    Falls back to every chunk for the session (unranked) if the vector index
    isn't ready yet or the query fails — chat degrades gracefully instead of
    hard-failing before index setup (scripts/create_vector_index.py) finishes.
    """
    settings = get_settings()
    collection = db[settings.vector_collection_name]

    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.vector_index_name,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": max(50, top_k * 10),
                "limit": top_k,
                "filter": {"session_id": session_id},
            }
        },
        {"$project": {"_id": 0, "text": 1, "column_name": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]

    try:
        results = [doc async for doc in collection.aggregate(pipeline)]
        if results:
            return [doc["text"] for doc in results]
    except Exception as exc:
        logger.warning(
            "Atlas Vector Search query failed (%s). Falling back to unranked schema chunks — "
            "confirm a vector index named '%s' exists on '%s.%s'.",
            exc, settings.vector_index_name, settings.mongodb_db_name, settings.vector_collection_name,
        )

    fallback_cursor = collection.find({"session_id": session_id}, {"_id": 0, "text": 1})
    return [doc["text"] async for doc in fallback_cursor]
