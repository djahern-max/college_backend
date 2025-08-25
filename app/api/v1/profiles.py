# app/api/v1/profiles.py
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileSummary,
    ProfileFieldUpdate,
    ProfileSection,
    ProfileCompletionStatus,
)

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return ProfileResponse.from_attributes(profile)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new profile for the current user"""
    profile_service = ProfileService(db)

    # Check if profile already exists
    existing_profile = profile_service.get_profile_by_user_id(current_user["id"])
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PATCH to update.",
        )

    profile = profile_service.create_profile(current_user["id"], profile_data)
    return ProfileResponse.from_attributes(profile)


@router.patch("/update", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile (creates if doesn't exist)"""
    profile_service = ProfileService(db)
    profile = profile_service.update_profile(current_user["id"], profile_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )

    return ProfileResponse.from_attributes(profile)


@router.patch("/field", response_model=ProfileResponse)
async def update_profile_field(
    field_update: ProfileFieldUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a single profile field (for auto-save functionality)"""
    profile_service = ProfileService(db)

    try:
        profile = profile_service.update_profile_field(
            current_user["id"], field_update.field_name, field_update.field_value
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile field",
            )

        return ProfileResponse.from_attributes(profile)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/summary", response_model=ProfileSummary)
async def get_profile_summary(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get profile completion summary"""
    profile_service = ProfileService(db)
    return profile_service.get_profile_summary(current_user["id"])


@router.get("/sections", response_model=Dict[str, ProfileCompletionStatus])
async def get_profile_sections(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get detailed completion status for each profile section"""
    profile_service = ProfileService(db)
    return profile_service.get_completion_status_by_section(current_user["id"])


@router.post("/complete", response_model=ProfileResponse)
async def complete_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Mark profile as completed"""
    profile_service = ProfileService(db)
    profile = profile_service.complete_profile(current_user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return ProfileResponse.from_attributes(profile)


@router.get("/view")
async def get_profile_view(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get formatted profile data for ProfileView component"""
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # Format profile data for frontend ProfileView component
    profile_view_data = {
        "profile": ProfileResponse.from_attributes(profile).model_dump(),
        "completion": {
            "profile_completed": profile.profile_completed,
            "completion_percentage": profile.completion_percentage,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "completed_at": profile.completed_at,
        },
        "sections": profile_service.get_completion_status_by_section(
            current_user["id"]
        ),
    }

    return profile_view_data


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete current user's profile"""
    profile_service = ProfileService(db)
    deleted = profile_service.delete_profile(current_user["id"])

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )


# Admin endpoints (optional - for user management)
@router.get("/user/{user_id}", response_model=ProfileResponse)
async def get_profile_by_user_id(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get profile by user ID (admin only)"""
    # TODO: Add admin authorization check
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return ProfileResponse.from_attributes(profile)
