"""
Authentication Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[dict] = None


class TokenData(BaseModel):
    """Token data schema."""
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class LogoutResponse(BaseModel):
    """Logout response schema."""
    message: str = "Successfully logged out"