# app/schemas/profile.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProfileBase(BaseModel):
    """Base profile schema with common fields"""

    # Basic Information
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

    # Test Scores
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)

    # Academic Interests
    intended_major: Optional[str] = None
    academic_interests: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None

    # Activities & Experience
    extracurricular_activities: Optional[List[str]] = None
    volunteer_experience: Optional[List[str]] = None
    volunteer_hours: Optional[int] = Field(None, ge=0)
    work_experience: Optional[Any] = None

    # Background & Demographics
    ethnicity: Optional[List[str]] = None
    first_generation_college: Optional[bool] = None
    household_income_range: Optional[str] = None

    # Location
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None

    # College Plans
    preferred_college_size: Optional[str] = None
    preferred_college_location: Optional[str] = None
    college_application_status: Optional[str] = None

    # Essays & Personal Statements
    personal_statement: Optional[str] = None
    leadership_experience: Optional[str] = None
    challenges_overcome: Optional[str] = None

    # Scholarship Preferences
    scholarship_types_interested: Optional[List[str]] = None
    application_deadline_preference: Optional[str] = None

    # Additional Information
    languages_spoken: Optional[List[str]] = None
    special_talents: Optional[List[str]] = None
    additional_info: Optional[str] = None

    # @validator("date_of_birth")
    # def validate_date_of_birth(cls, v):
    #     if v:
    #         try:
    #             datetime.strptime(v, "%Y-%m-%d")
    #         except ValueError:
    #             raise ValueError("Date of birth must be in YYYY-MM-DD format")
    #     return v

    # @validator("graduation_year")
    # def validate_graduation_year(cls, v):
    #     if v:
    #         current_year = datetime.now().year
    #         if v < current_year or v > current_year + 10:
    #             raise ValueError(
    #                 "Graduation year must be between current year and 10 years from now"
    #             )
    #     return v

    # @validator("phone_number")
    # def validate_phone_number(cls, v):
    #     if v:
    #         # Remove all non-digit characters for validation
    #         digits_only = "".join(filter(str.isdigit, v))
    #         if len(digits_only) < 10 or len(digits_only) > 15:
    #             raise ValueError("Phone number must contain 10-15 digits")
    #     return v


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""

    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating an existing profile"""

    pass


class ProfileSummary(BaseModel):
    """Schema for profile completion summary used by ProfileView"""

    profile_completed: bool
    completion_percentage: int
    has_basic_info: bool
    has_academic_info: bool
    has_personal_info: bool
    missing_fields: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "profile_completed": False,
                "completion_percentage": 65,
                "has_basic_info": True,
                "has_academic_info": True,
                "has_personal_info": False,
                "missing_fields": ["Personal Statement", "Leadership Experience"],
            }
        }


class ProfileResponse(ProfileBase):
    """Schema for profile API responses"""

    id: int
    user_id: int
    profile_completed: bool
    completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "high_school_name": "Lincoln High School",
                "graduation_year": 2025,
                "gpa": 3.8,
                "intended_major": "Computer Science",
                "sat_score": 1400,
                "academic_interests": ["Technology", "Mathematics"],
                "extracurricular_activities": ["Chess Club", "Robotics Team"],
                "personal_statement": "I am passionate about using technology to solve real-world problems...",
                "profile_completed": True,
                "completion_percentage": 85,
                "created_at": "2025-01-01T10:00:00Z",
                "updated_at": "2025-01-15T14:30:00Z",
                "completed_at": "2025-01-15T14:30:00Z",
            }
        }


class ProfileFieldUpdate(BaseModel):
    """Schema for updating a single profile field (used by ProfileBuilder auto-save)"""

    field_name: str = Field(..., min_length=1)
    field_value: Any

    class Config:
        json_schema_extra = {
            "example": {
                "field_name": "high_school_name",
                "field_value": "Lincoln High School",
            }
        }


class ProfileSection(BaseModel):
    """Schema for profile sections used by ProfileView display"""

    id: str
    title: str
    icon: str
    completed: bool
    fields: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "basic_info",
                "title": "Basic Information",
                "icon": "user",
                "completed": True,
                "fields": {
                    "high_school_name": "Lincoln High School",
                    "graduation_year": 2025,
                    "gpa": 3.8,
                },
            }
        }


class ProfileCompletionStatus(BaseModel):
    """Schema for profile completion status tracking"""

    section_name: str
    is_completed: bool
    completion_percentage: float
    required_fields: List[str]
    completed_fields: List[str]
    missing_fields: List[str]
