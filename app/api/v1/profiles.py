# app/api/v1/profiles.py - WORKS WITH USER OBJECTS + SETTINGS SUPPORT
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from app.models.institution import Institution

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import (
    ProfileUpdate,
    ProfileResponse,
    ProfileSimple,
    ProfileCreate,
    SettingsUpdate,
)
from app.schemas.institution import InstitutionResponse
from app.services.resume_parser import ResumeParser
from app.services.file_extractor import FileExtractor
from app.services.digitalocean_spaces import DigitalOceanSpaces
from app.schemas.resume import (
    ResumeUploadResponse,
    ParsedResumeData,
    ResumeParsingMetadata,
)
from app.core.config import settings
from app.models.user import User
from app.models.profile import UserProfile

router = APIRouter()


# ===========================
# BASIC PROFILE ENDPOINTS
# ===========================


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile_service = ProfileService(db)
    profile = profile_service.get_by_user_id(current_user.id)

    if not profile:
        # Create empty profile if doesn't exist
        profile = profile_service.create_profile(
            user_id=current_user.id, profile_data=ProfileCreate()
        )

    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    profile_service = ProfileService(db)

    # Try to update existing profile
    profile = profile_service.update_profile(current_user.id, profile_data)

    # If profile doesn't exist, create it
    if not profile:
        # Convert ProfileUpdate to ProfileCreate
        create_data = ProfileCreate(**profile_data.model_dump(exclude_unset=True))
        profile = profile_service.create_profile(current_user.id, create_data)

    return profile


@router.get("/me/matching-institutions")
async def get_matching_institutions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get institutions matching user's location preference
    Returns both institutions and total count
    """
    profile_service = ProfileService(db)

    # Get the profile first
    profile = profile_service.get_by_user_id(current_user.id)

    # If no profile or no location preference, return empty
    if not profile or not profile.location_preference:
        return {"institutions": [], "total": 0, "location_preference": None}

    # Get ALL matching institutions (no limit) to count them
    all_institutions = (
        db.query(Institution)
        .filter(Institution.state == profile.location_preference)
        .order_by(Institution.name)
        .all()
    )

    total_count = len(all_institutions)

    # Return limited set for display
    limited_institutions = all_institutions[:limit]

    return {
        "institutions": [
            InstitutionResponse.model_validate(i) for i in limited_institutions
        ],
        "total": total_count,
        "location_preference": profile.location_preference,
    }


# ===========================
# SETTINGS ENDPOINTS
# ===========================


@router.get("/me/settings", response_model=Dict[str, Any])
async def get_user_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get user settings

    Returns user preference settings like confetti_enabled
    """
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Return settings with defaults if not set
    return profile.settings or {"confetti_enabled": True}


@router.patch("/me/settings", response_model=Dict[str, Any])
async def update_user_settings(
    settings_update: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user settings

    Currently supports:
    - confetti_enabled: bool

    Example request body:
    {
        "confetti_enabled": false
    }
    """
    from sqlalchemy.orm.attributes import flag_modified

    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Get existing settings or initialize with defaults
    current_settings = profile.settings or {"confetti_enabled": True}

    # Update only provided settings (partial update)
    current_settings.update(settings_update)

    # Update profile with new settings
    profile.settings = current_settings

    # CRITICAL: Mark the JSONB field as modified so SQLAlchemy knows to update it
    flag_modified(profile, "settings")

    db.commit()
    db.refresh(profile)

    return {"message": "Settings updated successfully", "settings": profile.settings}


# ===========================
# FILE UPLOAD ENDPOINTS
# ===========================


@router.post("/me/upload-headshot")
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload profile headshot image

    Accepts JPG, PNG, WEBP up to 5MB
    """

    # Get user_id from User object
    user_id = current_user.id

    # Validate file type
    allowed_image_types = [".jpg", ".jpeg", ".png", ".webp"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed types: {', '.join(allowed_image_types)}",
        )

    # Validate file size (5MB max for images)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size_bytes = 5 * 1024 * 1024  # 5MB
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image too large. Maximum size: 5MB",
        )

    temp_file_path = None

    try:
        # Get or create user profile
        user_profile = (
            db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        # AUTO-CREATE PROFILE IF MISSING
        if not user_profile:
            profile_service = ProfileService(db)
            user_profile = profile_service.create_profile(
                user_id=user_id, profile_data=ProfileCreate()
            )

        # Create temp directory
        temp_dir = Path(settings.TEMP_UPLOAD_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Save file temporarily
        temp_file_path = temp_dir / f"headshot_{user_id}{file_extension}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload to Digital Ocean Spaces
        spaces = DigitalOceanSpaces()
        destination_path = spaces.generate_profile_path(
            user_id, f"headshot{file_extension}"
        )
        content_type = spaces.get_content_type(file.filename)

        image_url = spaces.upload_file(
            str(temp_file_path),
            destination_path,
            content_type=content_type,
            is_public=True,  # Profile images can be public
        )

        # Update user profile with image URL
        user_profile.profile_image_url = image_url
        db.commit()
        db.refresh(user_profile)

        # Clean up temp file
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)

        return {
            "status": "success",
            "profile_image_url": image_url,
            "message": "Profile image uploaded successfully",
        }

    except HTTPException:
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)
        raise
    except Exception as e:
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}",
        )


@router.post("/me/upload-resume-and-update", response_model=dict)
async def upload_resume_and_update_profile(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload resume, parse it, and AUTOMATICALLY update the profile with parsed data

    This is the main onboarding endpoint that:
    1. Uploads resume to DO Spaces
    2. Parses resume with AI
    3. Updates user profile with parsed data
    4. Returns the updated profile + scholarship matches

    Accepts PDF or DOCX files up to 10MB
    """

    user_id = current_user.id

    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_RESUME_EXTENSIONS)}",
        )

    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_RESUME_SIZE_MB}MB",
        )

    temp_file_path = None

    try:
        # Get or create user profile
        profile_service = ProfileService(db)
        user_profile = (
            db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        if not user_profile:
            user_profile = profile_service.create_profile(
                user_id=user_id, profile_data=ProfileCreate()
            )

        # Create temp directory
        temp_dir = Path(settings.TEMP_UPLOAD_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Save file temporarily
        temp_file_path = temp_dir / f"resume_{user_id}{file_extension}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from file
        extractor = FileExtractor()
        resume_text = extractor.extract_text(str(temp_file_path), file_extension)

        if not resume_text or len(resume_text) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract sufficient text from resume. Please ensure the file is readable.",
            )

        # Parse resume with AI
        parser = ResumeParser()
        parsed_result = parser.parse_resume(resume_text)

        # Extract metadata
        metadata = parsed_result.pop("_metadata", {})

        # Upload to Digital Ocean Spaces
        spaces = DigitalOceanSpaces()
        destination_path = spaces.generate_profile_path(user_id, "resume.pdf")
        content_type = spaces.get_content_type(file.filename)

        resume_url = spaces.upload_file(
            str(temp_file_path),
            destination_path,
            content_type=content_type,
            is_public=False,
        )

        # UPDATE PROFILE WITH PARSED DATA
        # Validate gpa_scale - only accept valid values, otherwise set to None
        raw_gpa_scale = parsed_result.get("gpa_scale")
        valid_gpa_scale = None
        if raw_gpa_scale in ["4.0", "5.0", "100", "weighted", "unweighted"]:
            valid_gpa_scale = raw_gpa_scale

        # Map parsed data to profile fields
        update_data = ProfileUpdate(
            state=parsed_result.get("state"),
            city=parsed_result.get("city"),
            zip_code=parsed_result.get("zip_code"),
            high_school_name=parsed_result.get("high_school_name"),
            graduation_year=parsed_result.get("graduation_year"),
            gpa=parsed_result.get("gpa"),
            gpa_scale=valid_gpa_scale,
            sat_score=parsed_result.get("sat_score"),
            act_score=parsed_result.get("act_score"),
            intended_major=parsed_result.get("intended_major"),
            resume_url=resume_url,
            # NEW FIELDS
            career_goals=parsed_result.get("career_goals"),
            volunteer_hours=parsed_result.get("volunteer_hours"),
            extracurriculars=parsed_result.get("extracurriculars"),
            work_experience=parsed_result.get("work_experience"),
            honors_awards=parsed_result.get("honors_awards"),
            skills=parsed_result.get("skills"),
        )

        # Update the profile
        updated_profile = profile_service.update_profile(user_id, update_data)

        # Clean up temp file
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)

        # Check if GPA exists
        needs_gpa = updated_profile.gpa is None

        # If GPA exists, get scholarship matches
        scholarship_matches = []
        if not needs_gpa:
            from app.services.scholarship import ScholarshipService

            scholarship_service = ScholarshipService(db)
            scholarship_matches = scholarship_service.find_by_gpa(
                gpa=updated_profile.gpa, limit=10
            )

        # Return comprehensive response
        return {
            "status": "success",
            "message": "Resume uploaded and profile updated successfully",
            "profile": ProfileResponse.model_validate(updated_profile),
            "resume_url": resume_url,
            "parsed_data": parsed_result,
            "metadata": metadata,
            "needs_gpa": needs_gpa,
            "scholarship_matches": (
                [
                    {
                        "id": s.id,
                        "title": s.title,
                        "organization": s.organization,
                        "amount_min": s.amount_min,
                        "amount_max": s.amount_max,
                        "deadline": str(s.deadline) if s.deadline else None,
                        "min_gpa": float(s.min_gpa) if s.min_gpa else None,
                    }
                    for s in scholarship_matches
                ]
                if scholarship_matches
                else []
            ),
        }

    except HTTPException:
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)
        raise
    except Exception as e:
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}",
        )
