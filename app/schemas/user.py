from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user fields shared across schemas"""

    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @validator("username")
    def username_validator(cls, v):
        """Validate username format"""
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


class UserCreate(UserBase):
    """Schema for creating new users"""

    password: str

    @validator("password")
    def password_validator(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if len(v) > 100:
            raise ValueError("Password must be less than 100 characters")
        return v

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

    @validator("username")
    def username_validator(cls, v):
        """Validate username format if provided"""
        if v is not None:
            if len(v) < 3:
                raise ValueError("Username must be at least 3 characters")
            if len(v) > 50:
                raise ValueError("Username must be less than 50 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError(
                    "Username can only contain letters, numbers, underscores, and hyphens"
                )
        return v


class UserResponse(UserBase):
    """Schema for user API responses"""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
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


class UserInDB(UserBase):
    """Schema for user data stored in database (internal use)"""

    id: int
    hashed_password: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Now resolve the forward reference in auth.py
from app.schemas.auth import LoginResponse

LoginResponse.model_rebuild()
