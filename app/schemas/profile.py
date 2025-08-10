"""
User Profile Pydantic schemas with privacy controls for API request/response validation.
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Literal
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


# Privacy-related types
VisibilityLevel = Literal["public", "private", "friends", "scholarship_only"]
ProfileVisibility = Literal["public", "private", "friends", "scholarship_only"]


class PrivacySettings(BaseModel):
    """Schema for field-level privacy settings."""
    # Personal Information
    phone: Optional[VisibilityLevel] = "private"
    date_of_birth: Optional[VisibilityLevel] = "private"
    profile_photo_url: Optional[VisibilityLevel] = "public"
    street_address: Optional[VisibilityLevel] = "private"
    city: Optional[VisibilityLevel] = "public"
    state: Optional[VisibilityLevel] = "public"
    zip_code: Optional[VisibilityLevel] = "private"
    
    # Academic Information
    high_school_name: Optional[VisibilityLevel] = "public"
    graduation_year: Optional[VisibilityLevel] = "public"
    gpa: Optional[VisibilityLevel] = "scholarship_only"
    class_rank: Optional[VisibilityLevel] = "private"
    class_size: Optional[VisibilityLevel] = "private"
    sat_score: Optional[VisibilityLevel] = "private"
    act_score: Optional[VisibilityLevel] = "private"
    
    # Athletic Information
    sports_played: Optional[VisibilityLevel] = "public"
    athletic_positions: Optional[VisibilityLevel] = "public"
    years_participated: Optional[VisibilityLevel] = "public"
    team_captain: Optional[VisibilityLevel] = "public"
    athletic_awards: Optional[VisibilityLevel] = "public"
    
    # Community Service & Activities
    volunteer_hours: Optional[VisibilityLevel] = "public"
    volunteer_organizations: Optional[VisibilityLevel] = "public"
    leadership_positions: Optional[VisibilityLevel] = "public"
    extracurricular_activities: Optional[VisibilityLevel] = "public"
    work_experience: Optional[VisibilityLevel] = "public"
    
    # Academic Achievements
    honors_courses: Optional[VisibilityLevel] = "public"
    academic_awards: Optional[VisibilityLevel] = "public"
    
    # College Plans
    intended_major: Optional[VisibilityLevel] = "public"
    college_preferences: Optional[VisibilityLevel] = "scholarship_only"
    career_goals: Optional[VisibilityLevel] = "public"
    
    # Essays
    personal_statement: Optional[VisibilityLevel] = "scholarship_only"
    career_essay: Optional[VisibilityLevel] = "scholarship_only"
    athletic_impact_essay: Optional[VisibilityLevel] = "scholarship_only"
    
    # References
    references: Optional[VisibilityLevel] = "scholarship_only"


class SportInfo(BaseModel):
    """Schema for sport information."""
    sport_name: str
    position: Optional[str] = None
    years_played: Optional[int] = None
    team_captain: Optional[bool] = False
    awards: Optional[List[str]] = []


class WorkExperience(BaseModel):
    """Schema for work experience."""
    job_title: str
    employer: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_current: Optional[bool] = False


class Reference(BaseModel):
    """Schema for references."""
    name: str
    title: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    relationship: Optional[str] = None  # "teacher", "coach", "counselor", etc.


class UserProfileBase(BaseModel):
    """Base user profile schema."""
    # Overall Privacy Settings
    profile_visibility: Optional[ProfileVisibility] = "private"
    allow_scholarship_matching: Optional[bool] = True
    
    # Personal Information
    middle_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    
    # Profile Photo
    profile_photo_url: Optional[str] = Field(None, max_length=500)
    profile_photo_filename: Optional[str] = Field(None, max_length=255)
    profile_photo_uploaded_at: Optional[datetime] = None
    
    # Address Information
    street_address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field("United States", max_length=100)
    
    # Academic Information
    high_school_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    gpa: Optional[Decimal] = Field(None, ge=0, le=4.0)
    class_rank: Optional[int] = Field(None, ge=1)
    class_size: Optional[int] = Field(None, ge=1)
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    
    # Athletic Information
    sports_played: Optional[List[str]] = []
    athletic_positions: Optional[Dict[str, str]] = {}
    years_participated: Optional[Dict[str, int]] = {}
    team_captain: Optional[List[str]] = []
    athletic_awards: Optional[List[str]] = []
    
    # Community Service & Activities
    volunteer_hours: Optional[int] = Field(None, ge=0)
    volunteer_organizations: Optional[List[str]] = []
    leadership_positions: Optional[List[str]] = []
    extracurricular_activities: Optional[List[str]] = []
    work_experience: Optional[List[Dict[str, Any]]] = []
    
    # Academic Achievements
    honors_courses: Optional[List[str]] = []
    academic_awards: Optional[List[str]] = []
    
    # College Plans
    intended_major: Optional[str] = Field(None, max_length=255)
    college_preferences: Optional[List[str]] = []
    career_goals: Optional[str] = None
    
    # Essays/Personal Statements
    personal_statement: Optional[str] = None
    career_essay: Optional[str] = None
    athletic_impact_essay: Optional[str] = None
    
    # References
    references: Optional[List[Dict[str, Any]]] = []
    
    # Privacy Settings
    field_privacy_settings: Optional[Dict[str, VisibilityLevel]] = None


class UserProfileCreate(UserProfileBase):
    """Schema for creating a user profile."""
    pass


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile (all fields optional)."""
    model_config = ConfigDict(extra='forbid')
    
    # Overall Privacy Settings
    profile_visibility: Optional[ProfileVisibility] = None
    allow_scholarship_matching: Optional[bool] = None
    
    # Personal Information
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    
    # Profile Photo
    profile_photo_url: Optional[str] = None
    profile_photo_filename: Optional[str] = None
    
    # Address Information
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    
    # Academic Information
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[Decimal] = None
    class_rank: Optional[int] = None
    class_size: Optional[int] = None
    sat_score: Optional[int] = None
    act_score: Optional[int] = None
    
    # Athletic Information
    sports_played: Optional[List[str]] = None
    athletic_positions: Optional[Dict[str, str]] = None
    years_participated: Optional[Dict[str, int]] = None
    team_captain: Optional[List[str]] = None
    athletic_awards: Optional[List[str]] = None
    
    # Community Service & Activities
    volunteer_hours: Optional[int] = None
    volunteer_organizations: Optional[List[str]] = None
    leadership_positions: Optional[List[str]] = None
    extracurricular_activities: Optional[List[str]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    
    # Academic Achievements
    honors_courses: Optional[List[str]] = None
    academic_awards: Optional[List[str]] = None
    
    # College Plans
    intended_major: Optional[str] = None
    college_preferences: Optional[List[str]] = None
    career_goals: Optional[str] = None
    
    # Essays/Personal Statements
    personal_statement: Optional[str] = None
    career_essay: Optional[str] = None
    athletic_impact_essay: Optional[str] = None
    
    # References
    references: Optional[List[Dict[str, Any]]] = None
    
    # Privacy Settings
    field_privacy_settings: Optional[Dict[str, VisibilityLevel]] = None


class UserProfilePrivacyUpdate(BaseModel):
    """Schema specifically for updating privacy settings."""
    profile_visibility: Optional[ProfileVisibility] = None
    allow_scholarship_matching: Optional[bool] = None
    field_privacy_settings: Optional[Dict[str, VisibilityLevel]] = None


class UserProfileResponse(UserProfileBase):
    """Schema for user profile responses with privacy filtering."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    profile_completed: bool
    completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserProfilePublicView(BaseModel):
    """Schema for public profile view (filtered based on privacy settings)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    profile_visibility: ProfileVisibility
    
    # Only fields marked as public will be included here
    # Fields will be dynamically filtered based on privacy settings
    profile_photo_url: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    sports_played: Optional[List[str]] = None
    athletic_positions: Optional[Dict[str, str]] = None
    years_participated: Optional[Dict[str, int]] = None
    team_captain: Optional[List[str]] = None
    athletic_awards: Optional[List[str]] = None
    volunteer_hours: Optional[int] = None
    volunteer_organizations: Optional[List[str]] = None
    leadership_positions: Optional[List[str]] = None
    extracurricular_activities: Optional[List[str]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    honors_courses: Optional[List[str]] = None
    academic_awards: Optional[List[str]] = None
    intended_major: Optional[str] = None
    career_goals: Optional[str] = None


class UserProfileScholarshipView(BaseModel):
    """Schema for scholarship application view (includes scholarship_only fields)."""
    model_config = ConfigDict(from_attributes=True)
    
    # Includes all public fields plus scholarship_only fields
    # This would be used when generating scholarship applications
    pass


class UserProfileSummary(BaseModel):
    """Summary schema for profile overview."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    profile_completed: bool
    completion_percentage: int
    profile_visibility: ProfileVisibility
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    sports_played: Optional[List[str]] = []
    updated_at: Optional[datetime] = None