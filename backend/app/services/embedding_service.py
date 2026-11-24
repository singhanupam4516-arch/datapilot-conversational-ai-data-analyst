"""Phase 3 — Hugging Face Embeddings, orchestrated through LangChain.

The same embedding model must be used for indexing (Phase 3) and for the
user's question at query time (Phase 4), or they won't land close together
in vector space.
"""
import logging

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.config import get_settings

logger = logging.getLogger(__name__)

_embedder: HuggingFaceEndpointEmbeddings | None = None


def get_embedder() -> HuggingFaceEndpointEmbeddings:
    """Lazily construct a single shared embeddings client for the process."""
    global _embedder
    if _embedder is None:
        settings = get_settings()
        _embedder = HuggingFaceEndpointEmbeddings(
            model=settings.embedding_model_name,
            huggingfacehub_api_token=settings.huggingfacehub_api_token,
        )
    return _embedder


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of schema chunks (Phase 3 indexing)."""
    if not texts:
        return []
    return await get_embedder().aembed_documents(texts)


async def embed_query(text: str) -> list[float]:
    """Embed a single user question (Phase 4 retrieval)."""
    return await get_embedder().aembed_query(text)
