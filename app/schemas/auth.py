# app/schemas/auth.py - FIXED
from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request with email and password"""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "claire@gmail.com", "password": "123456"}
        }


class UserResponseSimple(BaseModel):
    """Simple user response for login (avoids circular import)"""

    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Complete login response with user info and tokens"""

    access_token: str
    token_type: str
    expires_in: int
    user: UserResponseSimple

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
