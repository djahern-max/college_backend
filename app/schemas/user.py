# app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


# Extract validators as module-level functions
def validate_username(v: str) -> str:
    """Reusable username validation logic"""
    if not v:
        raise ValueError("Username is required")
    if len(v) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(v) > 50:
        raise ValueError("Username must be less than 50 characters")
    if not re.match(r"^[a-zA-Z0-9_-]+$", v):
        raise ValueError(
            "Username can only contain letters, numbers, underscores, and hyphens"
        )
    return v


def validate_password(v: str) -> str:
    """Reusable password validation logic"""
    if len(v) < 6:
        raise ValueError("Password must be at least 6 characters")
    if len(v) > 100:
        raise ValueError("Password must be less than 100 characters")
    return v


class UserBase(BaseModel):
    """Base user fields shared across schemas"""

    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_validator(cls, v):
        return validate_username(v)


class UserCreate(UserBase):
    """Schema for creating new users"""

    password: str

    @field_validator("password")
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "claire@gmail.com",
                "username": "CAhern",
                "first_name": "Claire",
                "last_name": "Ahern",
                "password": "123456",
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information"""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def username_validator(cls, v):
        """Validate username format if provided"""
        if v is not None:
            return validate_username(v)
        return v


class UserResponse(UserBase):
    """Schema for user API responses"""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "student@example.com",
                "username": "student123",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "created_at": "2025-01-01T10:00:00Z",
            }
        }
