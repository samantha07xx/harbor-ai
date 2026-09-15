"""Application settings for the Harbor backend."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    app_name: str = "Harbor API"
    qdrant_collection: str = "harbor_healthcare_chunks"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="HARBOR_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
