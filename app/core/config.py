# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "MagicScholar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/magicscholar_db"
    DB_PASSWORD: str = ""

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Domain Configuration
    DOMAIN: str = "localhost:3000"
    API_DOMAIN: str = "localhost:8000"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""

    # Digital Ocean Spaces Configuration - Using your existing variable names
    DIGITAL_OCEAN_SPACES_ACCESS_KEY: str = ""
    DIGITAL_OCEAN_SPACES_SECRET_KEY: str = ""
    DIGITAL_OCEAN_SPACES_ENDPOINT: str = ""
    DIGITAL_OCEAN_SPACES_BUCKET: str = ""
    DIGITAL_OCEAN_SPACES_REGION: str = ""
    IMAGE_CDN_BASE_URL: str = ""

    # CORS - Dynamic based on environment
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.ENVIRONMENT == "production":
            return [
                "https://magicscholar.com",
                "https://www.magicscholar.com",
            ]
        elif self.ENVIRONMENT == "staging":
            return ["https://staging.magicscholar.com", "http://localhost:3000"]
        else:  # development
            return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Frontend URL - Dynamic based on environment
    @property
    def FRONTEND_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            return "https://www.magicscholar.com"
        elif self.ENVIRONMENT == "staging":
            return "https://staging.magicscholar.com"
        else:  # development
            return "http://localhost:3000"

    # API Base URL - Dynamic based on environment
    @property
    def API_BASE_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            return "https://www.magicscholar.com"
        elif self.ENVIRONMENT == "staging":
            return "https://staging.magicscholar.com"
        else:  # development
            return "http://localhost:8000"

    # OAuth Settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""

    # TikTok OAuth
    TIKTOK_CLIENT_ID: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    TIKTOK_CLIENT_KEY: str = ""

    # OAuth Redirect URIs - Dynamic based on environment
    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        return f"{self.API_BASE_URL}/api/v1/oauth/google/callback"

    @property
    def LINKEDIN_REDIRECT_URI(self) -> str:
        return f"{self.API_BASE_URL}/api/v1/oauth/linkedin/callback"

    @property
    def TIKTOK_REDIRECT_URI(self) -> str:
        return f"{self.API_BASE_URL}/api/v1/oauth/tiktok/callback"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()
