"""MongoDB Atlas connection lifecycle (Motor async driver).

One cluster serves both the operational collections (uploads, chat_history)
and the Atlas Vector Search collection (schema_vectors) — per the project's
"single cloud database" architecture, there is no separate vector store.

The connection is intentionally non-fatal on failure: the API still boots
without a live MONGODB_URI (handy for local frontend dev against the
non-DB endpoints), and callers get a clear RuntimeError at request time
via `get_database()` instead of the whole process crashing on startup.
"""
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

logger = logging.getLogger(__name__)


class _MongoState:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


_state = _MongoState()


async def connect_to_mongo() -> None:
    settings = get_settings()
    try:
        _state.client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        _state.db = _state.client[settings.mongodb_db_name]
        await _state.client.admin.command("ping")
        logger.info("Connected to MongoDB Atlas database '%s'", settings.mongodb_db_name)
    except Exception as exc:
        _state.client = None
        _state.db = None
        logger.warning(
            "Could not connect to MongoDB (%s). Set a valid MONGODB_URI in .env — "
            "the API will otherwise respond with 503s on any DB-backed route.",
            exc,
        )


async def close_mongo_connection() -> None:
    if _state.client is not None:
        _state.client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    if _state.db is None:
        raise RuntimeError(
            "MongoDB is not connected. Check MONGODB_URI in your .env file and that your "
            "Atlas cluster's network access list allows this server's IP."
        )
    return _state.db
