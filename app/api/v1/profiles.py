# app/api/v1/profiles.py - REFACTORED WITH SERVICE LAYER
"""
Simplified profiles API - uses ProfileService for business logic
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import ProfileUpdate, ProfileResponse, ProfileSimple
from app.schemas.institution import InstitutionResponse  # You'll need this

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile_service = ProfileService(db)
    profile = profile_service.get_by_user_id(current_user["id"])

    if not profile:
        # Create empty profile if doesn't exist
        from app.schemas.profile import ProfileCreate

        profile = profile_service.create_profile(
            user_id=current_user["id"], profile_data=ProfileCreate()
        )

    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    profile_service = ProfileService(db)

    # Try to update existing profile
    profile = profile_service.update_profile(current_user["id"], profile_data)

    # If profile doesn't exist, create it
    if not profile:
        from app.schemas.profile import ProfileCreate

        # Convert ProfileUpdate to ProfileCreate
        create_data = ProfileCreate(**profile_data.model_dump(exclude_unset=True))
        profile = profile_service.create_profile(current_user["id"], create_data)

    return profile


@router.get("/me/matching-institutions", response_model=List[InstitutionResponse])
async def get_matching_institutions(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get institutions matching user's location preference

    Returns institutions in the state specified in user's location_preference field
    """
    profile_service = ProfileService(db)
    institutions = profile_service.find_matching_institutions(
        user_id=current_user["id"], limit=limit
    )

    if not institutions:
        # Check if user has set a location preference
        profile = profile_service.get_by_user_id(current_user["id"])
        if not profile or not profile.location_preference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please set your location_preference in your profile first",
            )

    return institutions
