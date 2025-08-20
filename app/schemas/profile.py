from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProfileBase(BaseModel):
    """Base profile fields - all the student information for scholarship matching"""
    
    # === BASIC INFORMATION ===
    date_of_birth: Optional[str] = None  # Format: YYYY-MM-DD
    phone_number: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    
    # === TEST SCORES ===
    sat_score: Optional[int] = None
    act_score: Optional[int] = None
    
    # === ACADEMIC INTERESTS ===
    intended_major: Optional[str] = None
    academic_interests: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None
    
    # === ACTIVITIES & EXPERIENCE ===
    extracurricular_activities: Optional[List[str]] = None
    volunteer_experience: Optional[List[str]] = None
    volunteer_hours: Optional[int] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    
    # === BACKGROUND & DEMOGRAPHICS ===
    ethnicity: Optional[List[str]] = None
    first_generation_college: Optional[bool] = None
    household_income_range: Optional[str] = None
    
    # === LOCATION ===
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    
    # === COLLEGE PLANS ===
    preferred_college_size: Optional[str] = None
    preferred_college_location: Optional[str] = None
    college_application_status: Optional[str] = None
    
    # === ESSAYS & PERSONAL STATEMENTS ===
    personal_statement: Optional[str] = None
    leadership_experience: Optional[str] = None
    challenges_overcome: Optional[str] = None
    
    # === SCHOLARSHIP PREFERENCES ===
    scholarship_types_interested: Optional[List[str]] = None
    application_deadline_preference: Optional[str] = None
    
    # === ADDITIONAL INFORMATION ===
    languages_spoken: Optional[List[str]] = None
    special_talents: Optional[List[str]] = None
    additional_info: Optional[str] = None
    
    # Validators for data quality
    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < current_year - 1 or v > current_year + 10:
                raise ValueError('Graduation year must be within reasonable range')
        return v
    
    @validator('gpa')
    def validate_gpa(cls, v):
        if v is not None:
            if v < 0.0 or v > 4.0:
                raise ValueError('GPA must be between 0.0 and 4.0')
        return v
    
    @validator('sat_score')
    def validate_sat_score(cls, v):
        if v is not None:
            if v < 400 or v > 1600:
                raise ValueError('SAT score must be between 400 and 1600')
        return v
    
    @validator('act_score')
    def validate_act_score(cls, v):
        if v is not None:
            if v < 1 or v > 36:
                raise ValueError('ACT score must be between 1 and 36')
        return v
    
    @validator('volunteer_hours')
    def validate_volunteer_hours(cls, v):
        if v is not None:
            if v < 0 or v > 10000:
                raise ValueError('Volunteer hours must be between 0 and 10,000')
        return v


class ProfileCreate(ProfileBase):
    """Schema for creating new profiles"""
    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating existing profiles"""
    pass


class ProfileResponse(ProfileBase):
    """Schema for profile API responses"""
    id: int
    user_id: int
    profile_completed: bool
    completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "high_school_name": "Lincoln High School",
                "graduation_year": 2024,
                "gpa": 3.8,
                "sat_score": 1450,
                "intended_major": "Computer Science",
                "academic_interests": ["Technology", "Mathematics"],
                "extracurricular_activities": ["Debate Team", "Robotics Club"],
                "state": "California",
                "city": "Los Angeles",
                "ethnicity": ["Hispanic/Latino"],
                "household_income_range": "$50,000-$75,000",
                "profile_completed": True,
                "completion_percentage": 85,
                "created_at": "2025-01-01T10:00:00Z",
                "updated_at": "2025-01-02T15:30:00Z",
                "completed_at": "2025-01-02T15:30:00Z"
            }
        }


class ProfileSummary(BaseModel):
    """Summary of profile completion status - used by frontend to show progress"""
    profile_completed: bool
    completion_percentage: int
    has_basic_info: bool
    has_academic_info: bool
    has_personal_info: bool
    missing_fields: List[str]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "profile_completed": False,
                "completion_percentage": 60,
                "has_basic_info": True,
                "has_academic_info": True,
                "has_personal_info": False,
                "missing_fields": [
                    "extracurricular_activities",
                    "volunteer_experience",
                    "personal_statement"
                ]
            }
        }


class ProfileFieldUpdate(BaseModel):
    """Schema for updating individual profile fields (for auto-save)"""
    field_name: str
    field_value: Any
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_name": "gpa",
                "field_value": 3.7
            }
        }
