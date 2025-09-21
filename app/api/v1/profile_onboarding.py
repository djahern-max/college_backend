# app/api/v1/profiles.py - UPDATED VERSION
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.profile import ProfileService
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    BasicProfileCreate,
    ActivityUpdate,
    DemographicsUpdate,
    AcademicEnhancement,
    EssayUpdate,
    CollegePreferences,
    ProfileProgressResponse,
    ContextualSuggestion,
)

router = APIRouter()

# =========================
# PROGRESSIVE ONBOARDING ENDPOINTS
# =========================


@router.post("/onboarding/basic", response_model=ProfileProgressResponse)
async def create_basic_profile(
    profile_data: BasicProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 1: Create basic profile with immediate scholarship matching"""
    try:
        profile_service = ProfileService(db)

        # Create basic profile
        profile = profile_service.create_basic_profile(current_user["id"], profile_data)

        # Get progress information
        progress = profile_service.get_completion_progress(current_user["id"])

        # For now, mock scholarship count (you'll integrate with your matching service)
        scholarship_count = _estimate_scholarship_matches(profile)

        return ProfileProgressResponse(
            profile_id=profile.id,
            completion_percentage=progress["completion_percentage"],
            tier=profile.profile_tier,
            scholarship_matches_count=scholarship_count,
            new_matches_unlocked=scholarship_count,
            next_steps=progress["next_steps"],
            progress_message=f"Great start! You've unlocked {scholarship_count} scholarship opportunities.",
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating basic profile: {str(e)}",
        )


@router.put("/enhance/activities", response_model=ProfileProgressResponse)
async def add_activities(
    activities_data: ActivityUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 2A: Add activities and leadership information"""
    try:
        profile_service = ProfileService(db)

        # Get previous scholarship count for comparison
        previous_profile = profile_service.get_profile_by_user_id(current_user["id"])
        previous_count = (
            _estimate_scholarship_matches(previous_profile) if previous_profile else 0
        )

        # Update activities
        profile = profile_service.add_activities(current_user["id"], activities_data)

        # Get updated counts and progress
        new_count = _estimate_scholarship_matches(profile)
        newly_unlocked = new_count - previous_count
        progress = profile_service.get_completion_progress(current_user["id"])

        return ProfileProgressResponse(
            profile_id=profile.id,
            completion_percentage=progress["completion_percentage"],
            tier=profile.profile_tier,
            scholarship_matches_count=new_count,
            new_matches_unlocked=newly_unlocked,
            next_steps=progress["next_steps"],
            progress_message=f"Excellent! Adding activities unlocked {newly_unlocked} new scholarship opportunities.",
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding activities: {str(e)}",
        )


@router.put("/enhance/demographics", response_model=ProfileProgressResponse)
async def add_demographics(
    demographics_data: DemographicsUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 2B: Add demographic information for targeted scholarships"""
    try:
        profile_service = ProfileService(db)

        previous_profile = profile_service.get_profile_by_user_id(current_user["id"])
        previous_count = (
            _estimate_scholarship_matches(previous_profile) if previous_profile else 0
        )

        profile = profile_service.add_demographics(
            current_user["id"], demographics_data
        )

        new_count = _estimate_scholarship_matches(profile)
        newly_unlocked = new_count - previous_count
        progress = profile_service.get_completion_progress(current_user["id"])

        # Generate personalized message based on demographics
        message = _get_demographic_unlock_message(demographics_data, newly_unlocked)

        return ProfileProgressResponse(
            profile_id=profile.id,
            completion_percentage=progress["completion_percentage"],
            tier=profile.profile_tier,
            scholarship_matches_count=new_count,
            new_matches_unlocked=newly_unlocked,
            next_steps=progress["next_steps"],
            progress_message=message,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding demographics: {str(e)}",
        )


@router.put("/enhance/academics", response_model=ProfileProgressResponse)
async def enhance_academics(
    academic_data: AcademicEnhancement,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 2C: Enhance academic information"""
    try:
        profile_service = ProfileService(db)

        previous_profile = profile_service.get_profile_by_user_id(current_user["id"])
        previous_count = (
            _estimate_scholarship_matches(previous_profile) if previous_profile else 0
        )

        profile = profile_service.enhance_academic_info(
            current_user["id"], academic_data
        )

        new_count = _estimate_scholarship_matches(profile)
        newly_unlocked = new_count - previous_count
        progress = profile_service.get_completion_progress(current_user["id"])

        return ProfileProgressResponse(
            profile_id=profile.id,
            completion_percentage=progress["completion_percentage"],
            tier=profile.profile_tier,
            scholarship_matches_count=new_count,
            new_matches_unlocked=newly_unlocked,
            next_steps=progress["next_steps"],
            progress_message=f"Academic profile enhanced! {newly_unlocked} additional opportunities unlocked.",
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enhancing academics: {str(e)}",
        )


@router.put("/essays", response_model=ProfileProgressResponse)
async def update_essay_status(
    essay_data: EssayUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update essay completion status"""
    try:
        profile_service = ProfileService(db)

        previous_profile = profile_service.get_profile_by_user_id(current_user["id"])
        previous_count = (
            _estimate_scholarship_matches(previous_profile) if previous_profile else 0
        )

        profile = profile_service.update_essay_status(current_user["id"], essay_data)

        new_count = _estimate_scholarship_matches(profile)
        newly_unlocked = new_count - previous_count
        progress = profile_service.get_completion_progress(current_user["id"])

        return ProfileProgressResponse(
            profile_id=profile.id,
            completion_percentage=progress["completion_percentage"],
            tier=profile.profile_tier,
            scholarship_matches_count=new_count,
            new_matches_unlocked=newly_unlocked,
            next_steps=progress["next_steps"],
            progress_message=f"Essay status updated! You now have access to {newly_unlocked} more essay-based scholarships.",
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating essay status: {str(e)}",
        )


@router.put("/preferences", response_model=ProfileProgressResponse)
async def add_college_preferences(
    preferences_data: CollegePreferences,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 3: Add college preferences"""
    try:
        profile_service = ProfileService(db)

        previous_profile = profile_service.get_profile_by_user_id(current_user["id"])
        previous_count = (
            _estimate_scholarship_matches(previous_profile) if previous_profile else 0
        )

        profile = profile_service.add_college_preferences(
            current_user["id"], preferences_data
        )

        new_count = _estimate_scholarship_matches(profile)
        newly_unlocked = new_count - previous_count
        progress = profile_service.get_completion_progress(current_user["id"])

        return ProfileProgressResponse(
            profile_id=profile.id,
            completion_percentage=progress["completion_percentage"],
            tier=profile.profile_tier,
            scholarship_matches_count=new_count,
            new_matches_unlocked=newly_unlocked,
            next_steps=progress["next_steps"],
            progress_message=f"College preferences added! Profile optimization complete with {new_count} total matches.",
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding preferences: {str(e)}",
        )


@router.get("/progress", response_model=Dict[str, Any])
async def get_profile_progress(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current profile completion status and recommendations"""
    try:
        profile_service = ProfileService(db)
        progress = profile_service.get_completion_progress(current_user["id"])

        profile = profile_service.get_profile_by_user_id(current_user["id"])
        if profile:
            current_matches = _estimate_scholarship_matches(profile)
            progress["scholarship_matches_count"] = current_matches
        else:
            progress["scholarship_matches_count"] = 0

        return progress

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting progress: {str(e)}",
        )


@router.get("/suggestions")
async def get_contextual_suggestions(
    context: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get contextual suggestions based on user behavior"""
    try:
        profile_service = ProfileService(db)
        suggestions = profile_service.get_contextual_suggestions(
            current_user["id"], context
        )

        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting suggestions: {str(e)}",
        )


# =========================
# TRADITIONAL CRUD ENDPOINTS
# =========================


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """CREATE - Create a comprehensive profile (traditional approach)"""
    try:
        profile_service = ProfileService(db)
        profile = profile_service.create_profile(current_user["id"], profile_data)
        return ProfileResponse.model_validate(profile)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating profile: {str(e)}",
        )


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """READ - Get current user's profile"""
    try:
        profile_service = ProfileService(db)
        profile = profile_service.get_profile_by_user_id(current_user["id"])

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        return ProfileResponse.model_validate(profile)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}",
        )


@router.patch("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """UPDATE - Update existing profile"""
    try:
        profile_service = ProfileService(db)
        profile = profile_service.update_profile(current_user["id"], profile_data)
        return ProfileResponse.model_validate(profile)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}",
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """DELETE - Remove user profile"""
    try:
        profile_service = ProfileService(db)
        profile_service.delete_profile(current_user["id"])

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}",
        )


# =========================
# HELPER FUNCTIONS
# =========================


def _estimate_scholarship_matches(profile) -> int:
    """Estimate scholarship matches based on profile completeness (placeholder)"""
    if not profile:
        return 0

    base_matches = 15  # Base scholarships for any profile

    # Add matches based on profile completeness
    if profile.gpa and profile.gpa >= 3.5:
        base_matches += 20
    if profile.sat_score and profile.sat_score >= 1300:
        base_matches += 15
    if profile.extracurricular_activities:
        base_matches += len(profile.extracurricular_activities) * 3
    if profile.volunteer_hours and profile.volunteer_hours > 50:
        base_matches += 10
    if profile.ethnicity:
        base_matches += 12  # Diversity scholarships
    if profile.first_generation_college:
        base_matches += 8
    if profile.has_personal_statement:
        base_matches += 25
    if profile.leadership_positions:
        base_matches += 15

    return min(base_matches, 150)  # Cap at reasonable number


def _get_demographic_unlock_message(
    demographics_data: DemographicsUpdate, newly_unlocked: int
) -> str:
    """Generate personalized message based on demographic information"""
    categories = []

    if demographics_data.first_generation_college:
        categories.append("first-generation college scholarships")
    if demographics_data.ethnicity:
        categories.append("diversity and inclusion scholarships")
    if demographics_data.military_connection:
        categories.append("military-affiliated scholarships")
    if demographics_data.rural_background:
        categories.append("rural community scholarships")

    if categories:
        category_text = ", ".join(categories)
        return f"Perfect! You've unlocked {newly_unlocked} new scholarships, including {category_text}."
    else:
        return f"Thanks for updating your profile! You now have access to {newly_unlocked} additional scholarships."
