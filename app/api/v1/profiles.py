# app/api/v1/profiles.py - WORKS WITH USER OBJECTS
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import (
    ProfileUpdate,
    ProfileResponse,
    ProfileSimple,
    ProfileCreate,
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


@router.get("/me/matching-institutions", response_model=List[InstitutionResponse])
async def get_matching_institutions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get institutions matching user's location preference

    Returns institutions in the state specified in user's location_preference field
    """
    profile_service = ProfileService(db)
    institutions = profile_service.find_matching_institutions(
        user_id=current_user.id, limit=limit
    )

    if not institutions:
        # Check if user has set a location preference
        profile = profile_service.get_by_user_id(current_user.id)
        if not profile or not profile.location_preference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please set your location_preference in your profile first",
            )

    return institutions


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


@router.post("/me/upload-resume", response_model=ResumeUploadResponse)
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload resume and automatically parse it to extract profile data

    Accepts PDF or DOCX files up to 10MB
    Returns parsed data that can be used to auto-fill the profile form
    """

    # Get user_id from User object
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
        user_profile = (
            db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        # AUTO-CREATE PROFILE IF MISSING
        if not user_profile:
            profile_service = ProfileService(db)
            user_profile = profile_service.create_profile(
                user_id=user_id, profile_data=ProfileCreate()
            )

        # Create temp directory if it doesn't exist
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
            is_public=False,  # Keep resumes private
        )

        # Update user profile with resume URL
        user_profile.resume_url = resume_url
        db.commit()
        db.refresh(user_profile)

        # Clean up temp file
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)

        # Return parsed data
        return ResumeUploadResponse(
            resume_url=resume_url,
            parsed_data=ParsedResumeData(**parsed_result),
            metadata=ResumeParsingMetadata(**metadata),
            message="Resume uploaded and parsed successfully. Review the data below and update your profile.",
        )

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
        # Map parsed data to profile fields
        update_data = ProfileUpdate(
            state=parsed_result.get("state"),
            city=parsed_result.get("city"),
            zip_code=parsed_result.get("zip_code"),
            high_school_name=parsed_result.get("high_school_name"),
            graduation_year=parsed_result.get("graduation_year"),
            gpa=parsed_result.get("gpa"),
            gpa_scale=parsed_result.get("gpa_scale"),
            sat_score=parsed_result.get("sat_score"),
            act_score=parsed_result.get("act_score"),
            intended_major=parsed_result.get("intended_major"),
            resume_url=resume_url,
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


@router.delete("/me/resume")
async def delete_resume(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Delete user's resume"""

    user_id = current_user.id
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not user_profile or not user_profile.resume_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No resume found"
        )

    try:
        # Extract path from URL
        resume_url = user_profile.resume_url
        file_path = resume_url.replace(settings.IMAGE_CDN_BASE_URL + "/", "")

        # Delete from Spaces
        spaces = DigitalOceanSpaces()
        spaces.delete_file(file_path)

        # Update database
        user_profile.resume_url = None
        db.commit()

        return {"status": "success", "message": "Resume deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting resume: {str(e)}",
        )


@router.patch("/me/gpa")
async def update_gpa(
    gpa: float,
    gpa_scale: str = "4.0",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user's GPA and return scholarship matches

    Use this when user doesn't have GPA in their resume
    """

    # Validate GPA
    if gpa < 0 or gpa > 5.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GPA must be between 0 and 5.0",
        )

    if gpa_scale not in ["4.0", "5.0", "100"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GPA scale must be 4.0, 5.0, or 100",
        )

    # Update profile
    profile_service = ProfileService(db)
    update_data = ProfileUpdate(gpa=gpa, gpa_scale=gpa_scale)
    profile = profile_service.update_profile(current_user.id, update_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # Get scholarship matches
    from app.services.scholarship import ScholarshipService

    scholarship_service = ScholarshipService(db)
    matches = scholarship_service.find_by_gpa(gpa=gpa, limit=10)

    return {
        "status": "success",
        "message": "GPA updated successfully",
        "profile": ProfileResponse.model_validate(profile),
        "scholarship_matches": [
            {
                "id": s.id,
                "title": s.title,
                "organization": s.organization,
                "amount_min": s.amount_min,
                "amount_max": s.amount_max,
                "deadline": str(s.deadline) if s.deadline else None,
                "min_gpa": float(s.min_gpa) if s.min_gpa else None,
                "website_url": s.website_url,
            }
            for s in matches
        ],
    }


@router.get("/me/scholarship-matches")
async def get_my_scholarship_matches(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get scholarship matches based on user's profile

    Currently matches based on GPA only
    Returns empty list if GPA not set
    """

    profile_service = ProfileService(db)
    profile = profile_service.get_by_user_id(current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first.",
        )

    # Check if GPA exists
    if not profile.gpa:
        return {
            "status": "incomplete_profile",
            "message": "Please add your GPA to see scholarship matches",
            "needs_gpa": True,
            "matches": [],
        }

    # Get scholarship matches
    from app.services.scholarship import ScholarshipService

    scholarship_service = ScholarshipService(db)
    matches = scholarship_service.find_by_gpa(gpa=profile.gpa, limit=limit)

    return {
        "status": "success",
        "message": f"Found {len(matches)} scholarship matches",
        "needs_gpa": False,
        "profile": {
            "gpa": profile.gpa,
            "gpa_scale": profile.gpa_scale,
            "graduation_year": profile.graduation_year,
            "intended_major": profile.intended_major,
        },
        "matches": [
            {
                "id": s.id,
                "title": s.title,
                "organization": s.organization,
                "scholarship_type": s.scholarship_type,
                "amount_min": s.amount_min,
                "amount_max": s.amount_max,
                "deadline": str(s.deadline) if s.deadline else None,
                "min_gpa": float(s.min_gpa) if s.min_gpa else None,
                "description": s.description,
                "website_url": s.website_url,
                "primary_image_url": s.primary_image_url,
            }
            for s in matches
        ],
    }
