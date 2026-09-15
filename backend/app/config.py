"""Application settings for the Harbor backend."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    app_name: str = "Harbor API"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "harbor_healthcare_chunks"
    embedding_provider: str | None = None
    embedding_model: str = "deterministic-test-embedding"
    embedding_dimensions: int = 16
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "HARBOR_OPENAI_API_KEY"),
    )
    openai_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "text-embedding-3-small"
    retrieval_mode: str = "demo"
    crawler_user_agent: str = "HarborBot/0.1 (+https://github.com/samantha07xx/harbor-ai)"
    crawler_timeout_seconds: float = 10.0
    cors_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="HARBOR_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
