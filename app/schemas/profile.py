# app/schemas/profile.py - UPDATED VERSION
from pydantic import BaseModel, Field, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.profile import IncomeRange, ProfileTier, CollegeSize


# =========================
# PROGRESSIVE ONBOARDING SCHEMAS
# =========================


class BasicProfileCreate(BaseModel):
    """Phase 1: Basic profile creation - minimum viable profile"""

    high_school_name: str = Field(
        ..., min_length=1, max_length=255, description="Full name of high school"
    )
    graduation_year: int = Field(
        ..., ge=2020, le=2030, description="Year of graduation"
    )
    gpa: float = Field(..., ge=0.0, le=5.0, description="Current GPA")
    gpa_scale: str = Field(default="4.0", description="GPA scale (4.0, 5.0, or 100)")
    intended_major: str = Field(
        ..., min_length=1, max_length=255, description="Intended college major"
    )
    state: str = Field(
        ..., min_length=2, max_length=50, description="State of residence"
    )

    # Test scores - at least one required
    sat_score: Optional[int] = Field(
        None, ge=400, le=1600, description="SAT total score"
    )
    act_score: Optional[int] = Field(
        None, ge=1, le=36, description="ACT composite score"
    )

    # Optional quick additions
    academic_interests: Optional[List[str]] = Field(
        default=[], description="Academic subjects of interest"
    )
    has_essays: bool = Field(
        default=False, description="Do you have any college essays written?"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "high_school_name": "Lincoln High School",
                "graduation_year": 2025,
                "gpa": 3.7,
                "gpa_scale": "4.0",
                "intended_major": "Computer Science",
                "state": "New Hampshire",
                "sat_score": 1340,
                "academic_interests": ["Mathematics", "Technology", "Science"],
                "has_essays": True,
            }
        }
    )


class ActivityUpdate(BaseModel):
    """Phase 2A: Activities and leadership enhancement"""

    extracurricular_activities: Optional[Dict[str, Any]] = Field(
        default={}, description="Extracurricular activities with details"
    )
    volunteer_experience: Optional[Dict[str, Any]] = Field(
        default={}, description="Volunteer work with hours and details"
    )
    volunteer_hours: Optional[int] = Field(
        None, ge=0, description="Total volunteer hours"
    )
    leadership_positions: Optional[Dict[str, Any]] = Field(
        default={}, description="Leadership roles and responsibilities"
    )
    sports_activities: Optional[Dict[str, Any]] = Field(
        default={}, description="Sports participation and achievements"
    )
    arts_activities: Optional[Dict[str, Any]] = Field(
        default={}, description="Arts, music, and creative activities"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "extracurricular_activities": {
                    "debate_team": {
                        "role": "Member",
                        "years": "2022-2025",
                        "hours_per_week": 6,
                        "achievements": ["Regional finalist", "Best speaker award"],
                    },
                    "robotics_club": {
                        "role": "Programming lead",
                        "years": "2023-2025",
                        "hours_per_week": 8,
                    },
                },
                "volunteer_experience": {
                    "local_food_bank": {
                        "role": "Food sorter",
                        "hours": 45,
                        "years": "2023-2024",
                    }
                },
                "volunteer_hours": 45,
                "leadership_positions": {
                    "student_council": {
                        "position": "Vice President",
                        "year": "2024-2025",
                        "responsibilities": ["Event planning", "Student advocacy"],
                    }
                },
            }
        }
    )


class DemographicsUpdate(BaseModel):
    """Phase 2B: Demographic information for targeted scholarships"""

    ethnicity: Optional[List[str]] = Field(
        default=[], description="Ethnic background (optional)"
    )
    gender: Optional[str] = Field(
        None, max_length=50, description="Gender identity (optional)"
    )
    first_generation_college: Optional[bool] = Field(
        None, description="First in family to attend college?"
    )
    household_income_range: Optional[IncomeRange] = Field(
        None, description="Household income range"
    )
    family_size: Optional[int] = Field(
        None, ge=1, le=20, description="Number of people in household"
    )

    # Additional demographic factors
    military_connection: bool = Field(
        default=False, description="Student or family military connection"
    )
    disability_status: Optional[bool] = Field(
        None, description="Student with disability status"
    )
    lgbtq_identification: Optional[bool] = Field(
        None, description="LGBTQ+ identification"
    )
    rural_background: Optional[bool] = Field(
        None, description="Rural community background"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ethnicity": ["Hispanic/Latino", "White"],
                "first_generation_college": True,
                "household_income_range": "50k_75k",
                "family_size": 4,
                "military_connection": False,
                "rural_background": True,
            }
        }
    )


class AcademicEnhancement(BaseModel):
    """Phase 2C: Enhanced academic information"""

    sat_math: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Math section score"
    )
    sat_verbal: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Verbal section score"
    )
    act_math: Optional[int] = Field(None, ge=1, le=36, description="ACT Math score")
    act_english: Optional[int] = Field(
        None, ge=1, le=36, description="ACT English score"
    )
    act_science: Optional[int] = Field(
        None, ge=1, le=36, description="ACT Science score"
    )
    act_reading: Optional[int] = Field(
        None, ge=1, le=36, description="ACT Reading score"
    )

    secondary_major: Optional[str] = Field(
        None, max_length=255, description="Second major of interest"
    )
    minor_interests: Optional[List[str]] = Field(
        default=[], description="Potential minors"
    )
    career_goals: Optional[List[str]] = Field(
        default=[], description="Career aspirations"
    )

    ap_courses: Optional[List[str]] = Field(
        default=[], description="AP courses taken/planned"
    )
    honors_courses: Optional[List[str]] = Field(
        default=[], description="Honors courses taken"
    )
    dual_enrollment: bool = Field(
        default=False, description="Dual enrollment participation"
    )
    class_rank: Optional[int] = Field(None, ge=1, description="Class rank")
    class_size: Optional[int] = Field(None, ge=1, description="Total class size")


class EssayUpdate(BaseModel):
    """Essay status tracking"""

    has_personal_statement: bool = Field(default=False)
    has_leadership_essay: bool = Field(default=False)
    has_challenges_essay: bool = Field(default=False)
    has_diversity_essay: bool = Field(default=False)
    has_community_service_essay: bool = Field(default=False)
    has_academic_interest_essay: bool = Field(default=False)


class CollegePreferences(BaseModel):
    """Phase 3: College preferences and constraints"""

    preferred_college_size: Optional[CollegeSize] = Field(
        None, description="Preferred college size"
    )
    preferred_states: Optional[List[str]] = Field(
        default=[], description="Preferred states for college"
    )
    max_tuition_budget: Optional[int] = Field(
        None, ge=0, description="Maximum tuition budget"
    )
    financial_aid_needed: Optional[bool] = Field(
        None, description="Financial aid requirement"
    )

    campus_setting: Optional[List[str]] = Field(
        default=[], description="Campus setting preferences"
    )
    religious_affiliation: Optional[str] = Field(
        None, max_length=100, description="Religious preference"
    )
    greek_life_interest: Optional[bool] = Field(
        None, description="Interest in Greek life"
    )
    research_opportunities_important: bool = Field(
        default=False, description="Research opportunities important"
    )
    study_abroad_interest: bool = Field(
        default=False, description="Study abroad interest"
    )


# =========================
# RESPONSE SCHEMAS
# =========================


class ProfileProgressResponse(BaseModel):
    """Response showing profile completion progress and recommendations"""

    profile_id: int
    completion_percentage: int
    tier: ProfileTier
    scholarship_matches_count: int
    new_matches_unlocked: int
    next_steps: List[Dict[str, str]]
    progress_message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_id": 123,
                "completion_percentage": 65,
                "tier": "enhanced",
                "scholarship_matches_count": 47,
                "new_matches_unlocked": 12,
                "next_steps": [
                    {
                        "action": "add_essays",
                        "title": "Upload Personal Statement",
                        "impact": "+25-30 new matches",
                        "time_estimate": "2 minutes",
                    }
                ],
                "progress_message": "Great progress! Adding your leadership experience unlocked 12 new scholarships.",
            }
        }
    )


class ContextualSuggestion(BaseModel):
    """Contextual suggestions based on user behavior"""

    field: str
    message: str
    impact: str
    priority: str
    privacy_note: Optional[str] = None


# =========================
# TRADITIONAL SCHEMAS (UPDATED)
# =========================


class ProfileBase(BaseModel):
    """Base profile fields - comprehensive model"""

    # Basic information
    high_school_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    gpa_scale: Optional[str] = Field("4.0", max_length=10)
    intended_major: Optional[str] = Field(None, max_length=255)

    # Contact info
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)

    # Academic information
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    sat_math: Optional[int] = Field(None, ge=200, le=800)
    sat_verbal: Optional[int] = Field(None, ge=200, le=800)
    act_math: Optional[int] = Field(None, ge=1, le=36)
    act_english: Optional[int] = Field(None, ge=1, le=36)
    act_science: Optional[int] = Field(None, ge=1, le=36)
    act_reading: Optional[int] = Field(None, ge=1, le=36)

    secondary_major: Optional[str] = Field(None, max_length=255)
    minor_interests: Optional[List[str]] = Field(default=[])
    academic_interests: Optional[List[str]] = Field(default=[])
    career_goals: Optional[List[str]] = Field(default=[])

    ap_courses: Optional[List[str]] = Field(default=[])
    honors_courses: Optional[List[str]] = Field(default=[])
    dual_enrollment: bool = Field(default=False)
    class_rank: Optional[int] = Field(None, ge=1)
    class_size: Optional[int] = Field(None, ge=1)

    # Activities (JSON fields)
    extracurricular_activities: Optional[Dict[str, Any]] = Field(default={})
    volunteer_experience: Optional[Dict[str, Any]] = Field(default={})
    volunteer_hours: Optional[int] = Field(None, ge=0)
    work_experience: Optional[Dict[str, Any]] = Field(default={})
    leadership_positions: Optional[Dict[str, Any]] = Field(default={})
    awards_honors: Optional[List[str]] = Field(default=[])
    competitions: Optional[Dict[str, Any]] = Field(default={})
    sports_activities: Optional[Dict[str, Any]] = Field(default={})
    arts_activities: Optional[Dict[str, Any]] = Field(default={})
    musical_instruments: Optional[List[str]] = Field(default=[])

    # Demographics
    ethnicity: Optional[List[str]] = Field(default=[])
    gender: Optional[str] = Field(None, max_length=50)
    first_generation_college: Optional[bool] = None
    household_income_range: Optional[IncomeRange] = None
    family_size: Optional[int] = Field(None, ge=1, le=20)
    military_connection: bool = Field(default=False)
    disability_status: Optional[bool] = None
    lgbtq_identification: Optional[bool] = None
    rural_background: Optional[bool] = None

    # Location
    state: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)

    # College preferences
    preferred_college_size: Optional[CollegeSize] = None
    preferred_states: Optional[List[str]] = Field(default=[])
    college_application_status: Optional[str] = Field(None, max_length=50)
    max_tuition_budget: Optional[int] = Field(None, ge=0)
    financial_aid_needed: Optional[bool] = None
    work_study_interest: bool = Field(default=False)

    campus_setting: Optional[List[str]] = Field(default=[])
    religious_affiliation: Optional[str] = Field(None, max_length=100)
    greek_life_interest: Optional[bool] = None
    research_opportunities_important: bool = Field(default=False)
    study_abroad_interest: bool = Field(default=False)

    # Essay status
    has_personal_statement: bool = Field(default=False)
    has_leadership_essay: bool = Field(default=False)
    has_challenges_essay: bool = Field(default=False)
    has_diversity_essay: bool = Field(default=False)
    has_community_service_essay: bool = Field(default=False)
    has_academic_interest_essay: bool = Field(default=False)

    # Scholarship preferences
    scholarship_types_interested: Optional[List[str]] = Field(default=[])
    application_deadline_preference: Optional[str] = Field(None, max_length=50)
    min_scholarship_amount: Optional[int] = Field(None, ge=0)
    renewable_scholarships_only: bool = Field(default=False)
    local_scholarships_priority: bool = Field(default=True)

    # Additional information
    languages_spoken: Optional[List[str]] = Field(default=[])
    special_talents: Optional[List[str]] = Field(default=[])
    certifications: Optional[List[str]] = Field(default=[])
    additional_notes: Optional[str] = None

    # Parent/guardian information
    parent_education_level: Optional[str] = Field(None, max_length=100)
    parent_occupation: Optional[str] = Field(None, max_length=100)
    parent_employer: Optional[str] = Field(None, max_length=255)

    household_income_range: Optional[IncomeRange] = Field(
        None,
        description="Household income range",
        alias="family_income_range",  # Accept both names
    )

    family_size: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Number of people in household",
        alias="household_size",  # Accept both names
    )

    model_config = ConfigDict(populate_by_name=True)  # Allow both field name and alias


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile - inherits all fields from ProfileBase"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "high_school_name": "Lincoln High School",
                "graduation_year": 2025,
                "gpa": 3.7,
                "intended_major": "Computer Science",
                "sat_score": 1340,
                "state": "New Hampshire",
                "city": "Manchester",
                "academic_interests": ["Mathematics", "Technology"],
                "extracurricular_activities": {
                    "robotics_club": {
                        "role": "Member",
                        "years": "2023-2025",
                        "hours_per_week": 4,
                    }
                },
                "volunteer_hours": 48,
                "languages_spoken": ["English", "Spanish"],
                "has_personal_statement": True,
            }
        }
    )


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile - all fields optional"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sat_score": 1450,
                "act_score": 33,
                "has_personal_statement": True,
                "volunteer_hours": 55,
                "leadership_positions": {
                    "student_council": {"position": "Secretary", "year": "2024-2025"}
                },
            }
        }
    )


class ProfileResponse(ProfileBase):
    """Schema for profile API responses - includes metadata"""

    # Database metadata
    id: int
    user_id: int
    profile_tier: ProfileTier
    profile_completed: bool
    completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
