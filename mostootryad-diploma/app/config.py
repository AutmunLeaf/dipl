from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/mostootryad"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Uploads
    UPLOAD_DIR: str = "uploads"

    # App
    APP_NAME: str = "Мостоотряд Диплом"
    DEBUG: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Получить кэшированные настройки приложения."""
    return Settings()
