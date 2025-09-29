# app/api/v1/profiles.py - New file needed for profiles endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService  # You'll need to create this
from app.schemas.profile import (
    ProfileResponse,
    ProfileCreate,
)  # You'll need these schemas

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile - returns 404 if no profile exists"""
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user["id"])  # FIXED

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return ProfileResponse.model_validate(profile)


@router.post("/", response_model=ProfileResponse)
async def create_user_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new profile for the current user"""
    profile_service = ProfileService(db)

    # Check if profile already exists
    existing_profile = profile_service.get_by_user_id(current_user["id"])
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update.",
        )

    # Create the profile
    profile = profile_service.create_profile(current_user["id"], profile_data)
    return ProfileResponse.model_validate(profile)


@router.put("/me", response_model=ProfileResponse)
async def update_user_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    profile_service = ProfileService(db)

    profile = profile_service.get_by_user_id(current_user["id"])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # Update the profile
    updated_profile = profile_service.update_profile(profile.id, profile_data)
    return ProfileResponse.model_validate(updated_profile)
