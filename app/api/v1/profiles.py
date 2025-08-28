# app/api/v1/profiles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """CREATE - Create a new profile for the current user"""
    profile_service = ProfileService(db)

    # Check if profile already exists
    existing_profile = profile_service.get_profile_by_user_id(current_user["id"])
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PATCH to update.",
        )

    profile = profile_service.create_profile(current_user["id"], profile_data)
    return ProfileResponse.from_orm(profile)


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """READ - Get current user's profile"""
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return ProfileResponse.from_orm(profile)


@router.patch("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """UPDATE - Update current user's profile"""
    profile_service = ProfileService(db)

    # Check if profile exists
    existing_profile = profile_service.get_profile_by_user_id(current_user["id"])
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Use POST to create a new profile.",
        )

    profile = profile_service.update_profile(current_user["id"], profile_data)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )

    return ProfileResponse.from_orm(profile)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """DELETE - Delete current user's profile"""
    profile_service = ProfileService(db)
    deleted = profile_service.delete_profile(current_user["id"])

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
