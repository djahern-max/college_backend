from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """Standard JWT token response"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Login request with email and password"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "securepassword123"
            }
        }


class LoginResponse(BaseModel):
    """Complete login response with user info and tokens"""
    access_token: str
    token_type: str
    expires_in: int
    user: "UserResponse"  # Forward reference - defined in user.py
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "email": "student@example.com",
                    "username": "student123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "created_at": "2025-01-01T10:00:00Z"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token"""
    refresh_token: str


class OAuthLoginRequest(BaseModel):
    """OAuth login request (for manual OAuth flow)"""
    provider: str
    code: str
    state: Optional[str] = None


class OAuthURL(BaseModel):
    """OAuth authorization URL response"""
    url: str
    state: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://accounts.google.com/o/oauth2/auth?client_id=...",
                "state": "abc123xyz789"
            }
        }


# This will be resolved after UserResponse is defined
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.user import UserResponse
