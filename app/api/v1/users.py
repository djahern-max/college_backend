from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user():
    """Register a new user"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "test_user",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z"
    }


@router.get("/me")
async def get_my_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's information"""
    return current_user


@router.patch("/me")
async def update_my_user_profile(current_user: dict = Depends(get_current_user)):
    """Update current user's information"""
    return {"message": "User profile updated"}


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get user by ID"""
    return {
        "id": user_id,
        "username": f"user_{user_id}",
        "email": f"user{user_id}@example.com"
    }
