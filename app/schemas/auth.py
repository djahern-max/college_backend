from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Login request with email and password"""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "claire@gmail.com", "password": "123456"}
        }


class LoginResponse(BaseModel):
    """Complete login response with user info and tokens"""

    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse  # No quotes needed with __future__ import

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "email": "claire@gmail.com",
                    "username": "CAhern",
                    "first_name": "Claire",
                    "last_name": "Ahern",
                    "is_active": True,
                    "created_at": "2025-01-01T10:00:00Z",
                },
            }
        }
