# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
from pydantic import validator

load_dotenv()


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "MagicScholar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database
    # NOTE:
    # - This is just a DEFAULT.
    # - .env (DATABASE_URL=...) will override this in all environments.
    # - For local dev, your .env currently points to unified_db:
    #   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/unified_db
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/unified_db"
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

    # Digital Ocean Spaces Configuration
    DIGITAL_OCEAN_SPACES_ACCESS_KEY: str = ""
    DIGITAL_OCEAN_SPACES_SECRET_KEY: str = ""
    DIGITAL_OCEAN_SPACES_ENDPOINT: str = ""
    DIGITAL_OCEAN_SPACES_BUCKET: str = ""
    DIGITAL_OCEAN_SPACES_REGION: str = ""
    IMAGE_CDN_BASE_URL: str = ""

    # File Upload Configuration
    MAX_RESUME_SIZE_MB: int = 10  # Maximum resume file size in MB
    ALLOWED_RESUME_EXTENSIONS: list = [".pdf", ".doc", ".docx"]
    TEMP_UPLOAD_DIR: str = "/tmp/uploads"  # Temporary directory for file processing

    ANTHROPIC_API_KEY: str = ""

    # OAuth Settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""

    @validator("GOOGLE_CLIENT_ID")
    def validate_google_config(cls, v, values):
        environment = values.get("ENVIRONMENT", "development")
        if environment == "production" and not v:
            raise ValueError("GOOGLE_CLIENT_ID is required in production")
        return v

    @validator("LINKEDIN_CLIENT_ID")
    def validate_linkedin_config(cls, v, values):
        environment = values.get("ENVIRONMENT", "development")
        if environment == "production" and not v:
            raise ValueError("LINKEDIN_CLIENT_ID is required in production")
        return v

    # CORS - Dynamic based on environment
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.ENVIRONMENT == "production":
            return [
                "https://magicscholar.com",
                "https://www.magicscholar.com",
                "https://app.magicscholar.com",
            ]
        elif self.ENVIRONMENT == "staging":
            return ["https://staging.magicscholar.com", "http://localhost:3000"]
        else:  # development
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]

    # Frontend URL - Dynamic based on environment
    @property
    def FRONTEND_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            # Use API_DOMAIN from .env for production
            return (
                f"https://{self.API_DOMAIN}"
                if self.API_DOMAIN
                else "https://app.magicscholar.com"
            )
        elif self.ENVIRONMENT == "staging":
            return "https://staging.magicscholar.com"
        else:  # development
            return "http://localhost:3000"

    # API Base URL - Dynamic based on environment
    @property
    def API_BASE_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            # Use API_DOMAIN from .env for production
            return (
                f"https://{self.API_DOMAIN}"
                if self.API_DOMAIN
                else "https://app.magicscholar.com"
            )
        elif self.ENVIRONMENT == "staging":
            return "https://staging.magicscholar.com"
        else:  # development
            return "http://localhost:8000"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()
