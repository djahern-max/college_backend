"""
Profile management endpoints.
"""
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies.auth import get_current_active_user, get_optional_user
from app.models.user import User
from app.schemas.profile import (
    UserProfileCreate, 
    UserProfileUpdate, 
    UserProfileResponse,
    UserProfileSummary
)
from app.services.profile import ProfileService

from pathlib import Path
import uuid
import os

UPLOAD_DIR = Path("uploads/profiles")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

router = APIRouter()


@router.get("/profiles/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile."""
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.post("/profiles", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new profile for the current user."""
    profile_service = ProfileService(db)
    
    # Check if user already has a profile
    existing_profile = await profile_service.get_by_user_id(current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PATCH to update."
        )
    
    return await profile_service.create(current_user.id, profile_data)


@router.patch("/profiles/update", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    profile_service = ProfileService(db)
    
    # Get existing profile or create one if it doesn't exist
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        # Auto-create profile if it doesn't exist
        create_data = UserProfileCreate(**profile_data.model_dump(exclude_unset=True))
        return await profile_service.create(current_user.id, create_data)
    
    return await profile_service.update(profile.id, profile_data)


@router.patch("/profiles/field", response_model=UserProfileResponse)
async def update_profile_field(
    field_updates: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update specific profile fields (for auto-save functionality)."""
    profile_service = ProfileService(db)
    
    # Get existing profile or create one if it doesn't exist
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        # Auto-create profile if it doesn't exist
        create_data = UserProfileCreate(**field_updates)
        return await profile_service.create(current_user.id, create_data)
    
    # Convert dict to UserProfileUpdate
    update_data = UserProfileUpdate(**field_updates)
    return await profile_service.update(profile.id, update_data)


@router.get("/profiles/summary", response_model=UserProfileSummary)
async def get_profile_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get profile completion summary."""
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        # Return empty summary if no profile exists
        return UserProfileSummary(
            id=0,
            user_id=current_user.id,
            profile_completed=False,
            completion_percentage=0,
            profile_visibility="private",  # Default value
            high_school_name=None,
            graduation_year=None,
            sports_played=[],
            updated_at=None
        )
    
    # Handle the case where profile_visibility might not exist in the database yet
    profile_visibility = getattr(profile, 'profile_visibility', 'private')
    profile_completed = getattr(profile, 'profile_completed', False)
    completion_percentage = getattr(profile, 'completion_percentage', 0)
    
    return UserProfileSummary(
        id=profile.id,
        user_id=profile.user_id,
        profile_completed=profile_completed,
        completion_percentage=completion_percentage,
        profile_visibility=profile_visibility,
        high_school_name=profile.high_school_name,
        graduation_year=profile.graduation_year,
        sports_played=profile.sports_played or [],
        updated_at=profile.updated_at
    )


@router.get("/profiles/user/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get another user's profile (with privacy filtering)."""
    profile_service = ProfileService(db)
    
    # Users can only view their own full profile or if they are superuser
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this profile"
        )
    
    profile = await profile_service.get_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.delete("/profiles", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user's profile."""
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    await profile_service.delete(profile.id)

@router.post("/profiles/complete", response_model=UserProfileResponse)
async def complete_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark profile as completed and redirect to profile view."""
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete the profile builder first."
        )
    
    # Mark as completed regardless of percentage
    completion_data = UserProfileUpdate(
        profile_completed=True,
        completion_percentage=max(profile.completion_percentage or 0, 80)  # Ensure at least 80%
    )
    
    updated_profile = await profile_service.update(profile.id, completion_data)
    return updated_profile


@router.get("/profiles/view", response_model=dict)
async def get_profile_view(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete profile view with all sections for display."""
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Organize profile data into sections for display
    profile_view = {
        "user": {
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
        },
        "basic_info": {
            "high_school_name": profile.high_school_name,
            "graduation_year": profile.graduation_year,
            "city": profile.city,
            "state": profile.state,
            "phone": profile.phone,
            "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        },
        "academics": {
            "gpa": float(profile.gpa) if profile.gpa else None,
            "sat_score": profile.sat_score,
            "act_score": profile.act_score,
            "honors_courses": profile.honors_courses or [],
            "academic_awards": profile.academic_awards or [],
        },
        "athletics": {
            "sports_played": profile.sports_played or [],
            "athletic_awards": profile.athletic_awards or [],
        },
        "community": {
            "volunteer_organizations": profile.volunteer_organizations or [],
            "volunteer_hours": profile.volunteer_hours,
        },
        "activities": {
            "extracurricular_activities": profile.extracurricular_activities or [],
            "intended_major": profile.intended_major,
            "career_goals": profile.career_goals,
        },
        "completion": {
            "profile_completed": profile.profile_completed,
            "completion_percentage": profile.completion_percentage,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        },
        "uploads": {
            "profile_photo_url": profile.profile_photo_url,
            "personal_statement": profile.personal_statement,
            "career_essay": profile.career_essay,
            "athletic_impact_essay": profile.athletic_impact_essay,
        }
    }
    
    return profile_view

@router.post("/profiles/upload/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload profile photo."""
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed."
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / "photos" / unique_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update profile with photo URL
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if profile:
        # Delete old photo if exists
        if profile.profile_photo_filename:
            old_path = UPLOAD_DIR / "photos" / profile.profile_photo_filename
            if old_path.exists():
                os.remove(old_path)
        
        # Update profile
        update_data = UserProfileUpdate(
            profile_photo_url=f"/uploads/profiles/photos/{unique_filename}",
            profile_photo_filename=unique_filename,
            profile_photo_uploaded_at=datetime.utcnow()
        )
        await profile_service.update(profile.id, update_data)
    
    return {
        "message": "Photo uploaded successfully",
        "photo_url": f"/uploads/profiles/photos/{unique_filename}"
    }


@router.post("/profiles/upload/essay")
async def upload_essay(
    essay_type: str,  # "personal_statement", "career_essay", "athletic_impact_essay"
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload essay/document."""
    valid_essay_types = ["personal_statement", "career_essay", "athletic_impact_essay"]
    if essay_type not in valid_essay_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid essay type. Must be one of: {', '.join(valid_essay_types)}"
        )
    
    # Validate file type
    if file.content_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOC, DOCX, and TXT files are allowed."
        )
    
    # Read and process content
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    # For text files, store content directly in database
    if file.content_type == "text/plain":
        essay_content = contents.decode('utf-8')
    else:
        # For other files, save to disk and store path
        file_extension = Path(file.filename).suffix
        unique_filename = f"{current_user.id}_{essay_type}_{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / "essays" / unique_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        essay_content = f"/uploads/profiles/essays/{unique_filename}"
    
    # Update profile
    profile_service = ProfileService(db)
    profile = await profile_service.get_by_user_id(current_user.id)
    
    if profile:
        update_data = UserProfileUpdate(**{essay_type: essay_content})
        await profile_service.update(profile.id, update_data)
    
    return {
        "message": f"{essay_type.replace('_', ' ').title()} uploaded successfully",
        "essay_type": essay_type
    }