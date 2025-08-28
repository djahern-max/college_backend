# app/schemas/profile.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ProfileCompletionStatus(BaseModel):
    """Schema for profile completion status by section"""

    section_name: str
    is_completed: bool
    completion_percentage: float
    required_fields: List[str]
    completed_fields: List[str]
    missing_fields: List[str]


class ProfileBase(BaseModel):
    """Base profile schema with all available fields"""

    # Basic Information
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = Field(
        None, ge=0.0, le=5.0
    )  # Allows weighted GPA, matches Float in model

    # Test Scores
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)

    # Academic Information
    intended_major: Optional[str] = None
    academic_interests: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None

    # Activities & Experience
    extracurricular_activities: Optional[List[str]] = None
    volunteer_experience: Optional[List[str]] = None
    volunteer_hours: Optional[int] = Field(None, ge=0)
    work_experience: Optional[Any] = None  # JSON field - can be dict or list

    # Background & Demographics
    ethnicity: Optional[List[str]] = None
    first_generation_college: Optional[bool] = None
    household_income_range: Optional[str] = None

    # Location Information
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None

    # College Preferences
    preferred_college_size: Optional[str] = None
    preferred_college_location: Optional[str] = None
    college_application_status: Optional[str] = None

    # Essays & Personal Statements
    personal_statement: Optional[str] = None
    leadership_experience: Optional[str] = None
    challenges_overcome: Optional[str] = None

    # Scholarship Information
    scholarship_types_interested: Optional[List[str]] = None
    application_deadline_preference: Optional[str] = None

    # Additional Information
    languages_spoken: Optional[List[str]] = None
    special_talents: Optional[List[str]] = None
    additional_info: Optional[str] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile - accepts all fields from ProfileBase"""

    class Config:
        json_schema_extra = {
            "example": {
                "high_school_name": "Exeter High School",
                "graduation_year": 2026,
                "gpa": 4.49,
                "intended_major": "Fashion Marketing",
                "academic_interests": [
                    "Fashion Marketing",
                    "Digital Marketing",
                    "International Business",
                ],
                "extracurricular_activities": [
                    "Varsity Volleyball",
                    "French Honor Society",
                    "DECA",
                ],
                "volunteer_hours": 48,
                "state": "New Hampshire",
                "city": "Exeter",
                "zip_code": "03833",
                "languages_spoken": ["English", "French"],
                "special_talents": [
                    "Volleyball - College Recruitment Level",
                    "French Language Proficiency",
                ],
            }
        }


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile - all fields optional, inherits from ProfileBase"""

    class Config:
        json_schema_extra = {
            "example": {
                "sat_score": 1450,
                "act_score": 33,
                "personal_statement": "Updated personal statement reflecting recent achievements...",
                "volunteer_hours": 55,
            }
        }


class ProfileResponse(ProfileBase):
    """Schema for profile API responses - includes all ProfileBase fields plus metadata"""

    # Database metadata fields
    id: int
    user_id: int
    profile_completed: bool
    completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        # Use model_config for Pydantic v2
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Compatibility method for older Pydantic versions"""
        return cls.model_validate(obj)
