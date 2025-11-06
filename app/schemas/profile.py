# app/schemas/profile.py - UPDATED VERSION WITH EXTRACURRICULARS IN UPDATE

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===========================
# SUPPORTING SCHEMAS
# ===========================


class ExtracurricularActivity(BaseModel):
    """Schema for extracurricular activity"""

    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    years_active: Optional[str] = None


class WorkExperience(BaseModel):
    """Schema for work experience"""

    title: str
    organization: str
    dates: Optional[str] = None
    description: Optional[str] = None


# ===========================
# MAIN PROFILE SCHEMAS
# ===========================


class ProfileBase(BaseModel):
    """Base profile schema with common fields"""

    # Location
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)

    # Academic info
    high_school_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2035)
    gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    gpa_scale: Optional[str] = Field(
        None, max_length=20
    )  # "4.0", "5.0", "100", "weighted", "unweighted"
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    intended_major: Optional[str] = Field(None, max_length=255)

    # Career & Activities
    career_goals: Optional[str] = Field(None, max_length=500)
    volunteer_hours: Optional[int] = Field(None, ge=0)
    extracurriculars: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    honors_awards: Optional[List[str]] = None
    skills: Optional[List[str]] = None

    # Matching Criteria
    location_preference: Optional[str] = Field(None, min_length=2, max_length=2)

    # File uploads
    profile_image_url: Optional[str] = Field(None, max_length=500)
    resume_url: Optional[str] = Field(None, max_length=500)


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""

    pass


class ProfileUpdate(ProfileBase):
    """
    Schema for updating a profile - all fields optional, inherits from ProfileBase

    IMPORTANT: Now includes extracurriculars, work_experience, honors_awards, and skills
    so users can manually edit these fields even if not parsed from resume.
    """

    pass


class ProfileSimple(BaseModel):
    """Simplified profile response without nested relationships"""

    id: int
    user_id: int
    state: Optional[str] = None
    city: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    location_preference: Optional[str] = None


class ProfileResponse(ProfileBase):
    """Schema for profile API responses"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
