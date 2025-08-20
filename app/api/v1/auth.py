from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_refresh_token
)
from app.models.user import User
from app.schemas.auth import LoginResponse, Token, RefreshTokenRequest
from app.schemas.user import UserResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    
    # For now, return a mock successful login response
    # In the format your frontend expects
    mock_user = {
        "id": 1,
        "email": form_data.username,  # OAuth2PasswordRequestForm uses username for email
        "username": "testuser123",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z"
    }
    
    # Create access token with user ID (number) not username
    access_token = create_access_token(subject=mock_user["id"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,
        "user": mock_user
    }


@router.get("/me")
async def get_current_user_info():
    """Get current user info"""
    # Return mock user data for now
    return {
        "id": 1,
        "email": "john@example.com",
        "username": "testuser123",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z"
    }


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logout successful"}