# app/api/v1/profiles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.profile import UserProfile
from app.models.institution import Institution

router = APIRouter()


class ProfileUpdate(BaseModel):
    """Simple update model - only state for now"""

    state: Optional[str] = None
    preferred_states: Optional[list[str]] = None


class ProfileResponse(BaseModel):
    """Simple response model"""

    user_id: int
    state: Optional[str] = None
    preferred_states: Optional[list[str]] = None  # Add this
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    intended_major: Optional[str] = None
    academic_interests: Optional[list] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
    )

    if not profile:
        # Return empty profile structure
        return ProfileResponse(
            user_id=current_user["id"],
            state=None,
            high_school_name=None,
            graduation_year=None,
            gpa=None,
            intended_major=None,
            academic_interests=None,
        )

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
        profile = UserProfile(
            user_id=current_user["id"], profile_tier="basic", profile_completed=False
        )
        db.add(profile)

    # Update only provided fields
    if profile_data.preferred_states is not None:
        profile.preferred_states = profile_data.preferred_states

    db.commit()
    db.refresh(profile)

    return profile


@router.get("/school-matches")
async def get_school_matches(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get school matches based on profile state and preferred states"""

    # Get profile
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
    )

    # Build list of states to match
    states_to_match = []
    if profile and profile.state:
        states_to_match.append(profile.state)
    if profile and profile.preferred_states:
        states_to_match.extend(profile.preferred_states)

    # Remove duplicates
    states_to_match = list(set(states_to_match))

    if not states_to_match:
        return {
            "matches": [],
            "total": 0,
            "message": "Add your state preferences to see school matches",
        }

    # Get schools in selected states
    schools = (
        db.query(Institution)
        .filter(Institution.state.in_(states_to_match))
        .limit(50)
        .all()
    )

    # Format response
    matches = []
    for school in schools:
        matches.append(
            {
                "id": school.id,
                "name": school.name,
                "city": school.city,
                "state": school.state,
                "match_score": 100,  # Simple: in preferred states = 100% match
            }
        )

    return {"matches": matches, "total": len(matches)}
