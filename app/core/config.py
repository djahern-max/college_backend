from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "CampusConnect"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database - Updated for campus_connect
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/campus_connect"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Domain Configuration
    DOMAIN: str = "localhost:3000"  # Will be campusconnect.com in production
    API_DOMAIN: str = "localhost:8000"  # Will be api.campusconnect.com in production
    
    # CORS - Dynamic based on environment
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.ENVIRONMENT == "production":
            return [
                "https://campusconnect.com",
                "https://www.campusconnect.com"
            ]
        elif self.ENVIRONMENT == "staging":
            return [
                "https://staging.campusconnect.com",
                "http://localhost:3000"
            ]
        else:  # development
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ]
    
    # Frontend URL - Dynamic based on environment
    @property
    def FRONTEND_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            return "https://campusconnect.com"
        elif self.ENVIRONMENT == "staging":
            return "https://staging.campusconnect.com"
        else:  # development
            return "http://localhost:3000"
    
    # API Base URL - Dynamic based on environment
    @property
    def API_BASE_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            return "https://api.campusconnect.com"
        elif self.ENVIRONMENT == "staging":
            return "https://api-staging.campusconnect.com"
        else:  # development
            return "http://localhost:8000"
    
    # OAuth Settings - Dynamic redirect URIs
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        return f"{self.API_BASE_URL}/api/v1/oauth/google/callback"
    
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    
    @property
    def LINKEDIN_REDIRECT_URI(self) -> str:
        return f"{self.API_BASE_URL}/api/v1/oauth/linkedin/callback"
    
    TIKTOK_CLIENT_ID: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    
    @property
    def TIKTOK_REDIRECT_URI(self) -> str:
        return f"{self.API_BASE_URL}/api/v1/oauth/tiktok/callback"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()