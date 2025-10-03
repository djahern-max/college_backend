# app/api/v1/profiles.py - CLEANED UP
"""
Simplified profiles API - only uses fields that exist in minimal model
Removed references to dropped fields
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.schemas.profile import ProfileUpdate, ProfileResponse, ProfileSimple

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
    )

    if not profile:
        # Create empty profile if doesn't exist
        profile = UserProfile(user_id=current_user["id"])
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
    )

    # Create if doesn't exist
    if not profile:
        profile = UserProfile(user_id=current_user["id"])
        db.add(profile)

    # Update fields (only if provided in request)
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile


@router.get("/school-matches")
async def get_school_matches(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get school matches based on profile state
    Simple matching: shows schools in user's state
    """

    # Get profile
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
    )

    if not profile or not profile.state:
        return {
            "matches": [],
            "total": 0,
            "message": "Add your state to your profile to see school matches",
        }

    # Get schools in user's state
    schools = (
        db.query(Institution).filter(Institution.state == profile.state).limit(50).all()
    )

    # Format response
    matches = []
    for school in schools:
        matches.append(
            {
                "id": school.id,
                "ipeds_id": school.ipeds_id,
                "name": school.name,
                "city": school.city,
                "state": school.state,
                "control_type": school.control_type.value,
                "image_url": school.primary_image_url,
                "match_score": 100,  # In user's state = 100% match
            }
        )

    return {
        "matches": matches,
        "total": len(matches),
        "user_state": profile.state,
    }
