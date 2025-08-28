# app/api/v1/profiles.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Any


from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileSummary,
    ProfileFieldUpdate,
)

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile (creates empty one if doesn't exist)"""
    profile_service = ProfileService(db)
    profile = profile_service.get_or_create_profile(current_user["id"])
    return ProfileResponse.from_orm(profile)


@router.post("/", response_model=ProfileResponse)
async def create_or_update_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new profile or update existing one (upsert pattern)"""
    profile_service = ProfileService(db)
    profile = profile_service.upsert_profile(current_user["id"], profile_data)
    return ProfileResponse.from_orm(profile)


@router.patch("/", response_model=ProfileResponse)
async def update_profile_fields(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update specific profile fields (creates profile if doesn't exist)"""
    profile_service = ProfileService(db)
    profile = profile_service.update_profile_fields(current_user["id"], profile_data)
    return ProfileResponse.from_orm(profile)


@router.patch("/field", response_model=ProfileResponse)
async def update_single_field(
    field_update: ProfileFieldUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a single profile field (for auto-save functionality)"""
    profile_service = ProfileService(db)

    try:
        profile = profile_service.update_single_field(
            current_user["id"], field_update.field_name, field_update.field_value
        )
        return ProfileResponse.from_orm(profile)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/summary", response_model=ProfileSummary)
async def get_profile_summary(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get profile completion summary"""
    profile_service = ProfileService(db)
    return profile_service.get_profile_summary(current_user["id"])


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
