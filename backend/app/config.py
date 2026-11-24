"""Centralized application settings, loaded from environment variables / .env.

Every setting has a safe default so the app can still import and boot (e.g.
for local frontend development or automated tests) without a fully
configured .env — real Atlas/Hugging Face calls will simply fail clearly
at request time if left unconfigured, instead of crashing the whole server.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # MongoDB Atlas
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "conversational_data_analyst"

    # Hugging Face Inference API
    huggingfacehub_api_token: str = ""
    embedding_model_name: str = "BAAI/bge-large-en-v1.5"
    llm_model_name: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # Collections / vector index
    vector_index_name: str = "schema_vector_index"
    vector_collection_name: str = "schema_vectors"
    uploads_collection_name: str = "uploads"
    chat_history_collection_name: str = "chat_history"

    # App
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_size_mb: int = 25
    environment: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
