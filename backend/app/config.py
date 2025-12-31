"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://stakeholder_sim:devpassword@localhost:5432/stakeholder_sim"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API Keys
    anthropic_api_key: str = ""

    # Auth (Mock for MVP)
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
