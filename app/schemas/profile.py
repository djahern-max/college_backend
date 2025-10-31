# app/schemas/profile.py - UPDATE YOUR EXISTING SCHEMAS

from pydantic import BaseModel, Field, validator, computed_field
from typing import Optional
from datetime import datetime
from pydantic.config import ConfigDict


class ProfileBase(BaseModel):
    """Base profile schema with common fields"""

    # Location
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)

    # Academic info
    high_school_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    gpa_scale: Optional[str] = Field(None, pattern="^(4.0|5.0|100)$")
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    intended_major: Optional[str] = Field(None, max_length=255)

    # Matching Criteria
    location_preference: Optional[str] = Field(None, min_length=2, max_length=2)

    @validator("state", "location_preference")
    def validate_state_codes(cls, v):
        """Validate and uppercase state codes"""
        if v:
            return v.upper()
        return v


class ProfileCreate(BaseModel):
    """Schema for creating a new profile"""

    state: Optional[str] = Field(None, max_length=2, min_length=2)
    city: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)
    high_school_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    gpa_scale: Optional[str] = Field(None, pattern="^(4.0|5.0|100)$")
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    intended_major: Optional[str] = Field(None, max_length=255)
    location_preference: Optional[str] = Field(None, max_length=2, min_length=2)
    profile_image_url: Optional[str] = Field(None, max_length=500)  # NEW
    resume_url: Optional[str] = Field(None, max_length=500)  # NEW


class ProfileUpdate(BaseModel):
    """Schema for updating a profile - all fields optional"""

    state: Optional[str] = Field(None, max_length=2, min_length=2)
    city: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)
    high_school_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    gpa_scale: Optional[str] = Field(None, pattern="^(4.0|5.0|100)$")
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    intended_major: Optional[str] = Field(None, max_length=255)
    location_preference: Optional[str] = Field(None, max_length=2, min_length=2)
    profile_image_url: Optional[str] = Field(None, max_length=500)  # NEW
    resume_url: Optional[str] = Field(None, max_length=500)  # NEW
    profile_image_url: Optional[str] = None
    resume_url: Optional[str] = None


class ProfileResponse(BaseModel):
    """Schema for profile API responses"""

    id: int
    user_id: int
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    gpa_scale: Optional[str] = None
    sat_score: Optional[int] = None
    act_score: Optional[int] = None
    intended_major: Optional[str] = None
    location_preference: Optional[str] = None
    profile_image_url: Optional[str] = None  # NEW
    resume_url: Optional[str] = None  # NEW
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile_image_url: Optional[str] = None
    resume_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""

    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile - all fields optional"""

    pass


class ProfileResponse(ProfileBase):
    """Schema for profile API responses"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProfileSimple(BaseModel):
    """Simplified profile for listings"""

    id: int
    user_id: int
    state: Optional[str]
    graduation_year: Optional[int]
    gpa: Optional[float]
    intended_major: Optional[str]
    location_preference: Optional[str]  # Include in simple view for matching

    class Config:
        from_attributes = True
