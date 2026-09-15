"""Application settings for the Harbor backend."""

from functools import lru_cache

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
