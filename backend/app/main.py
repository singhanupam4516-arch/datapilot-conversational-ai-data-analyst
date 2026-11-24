"""FastAPI application entrypoint — wires together all four pipeline phases.

Phase 1 (upload.py) -> Phase 2 (eda.py) -> Phase 3 (folded into upload.py's
indexing step) -> Phase 4 (chat.py), with sessions.py serving chat history.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.config import get_settings
from app.routers import chat, eda, sessions, upload
from app.utils.logger import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Imported as a module (not `from app.database import connect_to_mongo`)
    # so tests can patch app.database.connect_to_mongo and have it actually
    # take effect here — a `from ... import` binds its own local reference
    # at import time that a later patch on the source module can't reach.
    await database.connect_to_mongo()
    yield
    await database.close_mongo_connection()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="DataPilot — Conversational AI Data Analyst API",
        description=(
            "Upload a spreadsheet, get instant automated EDA, and ask natural-language "
            "questions answered live by an open-source LLM writing and running Pandas code."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        # Any *.vercel.app deployment (production + preview URLs) may call the API.
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(upload.router, prefix="/api", tags=["Phase 1 — Ingestion"])
    app.include_router(eda.router, prefix="/api", tags=["Phase 2 — EDA"])
    app.include_router(chat.router, prefix="/api", tags=["Phase 4 — Conversational Loop"])
    app.include_router(sessions.router, prefix="/api", tags=["Sessions"])

    @app.get("/api/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "ok", "service": "datapilot-backend", "environment": settings.environment}

    return app


app = create_app()
