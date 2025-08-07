"""
Application settings and configuration.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Application Settings
    APP_NAME: str = "College Backend API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/college_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "college_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    LOG_LEVEL: str = "INFO"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
