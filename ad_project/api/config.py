"""Environment-backed configuration for the backend."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = "postgresql://ad_user:ad_password@localhost:5432/ad_project"
    jwt_secret_key: str = Field(
        default="development-only-change-me",
        min_length=16,
    )
    jwt_access_token_minutes: int = Field(default=30, ge=5, le=1440)
    enable_background_collection: bool = False
    collection_interval_seconds: int = Field(default=60, ge=10, le=86400)
    admin_email: Optional[str] = None
    admin_password: Optional[str] = Field(default=None, min_length=12)
    api_allowed_origins: str = "http://localhost:3000"
    require_https: bool = False
    login_rate_limit_per_minute: int = Field(default=5, ge=1, le=100)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
