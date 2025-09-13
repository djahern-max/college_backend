# app/schemas/scholarship.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===========================
# ENUMS
# ===========================


class ScholarshipType(str, Enum):
    ACADEMIC_MERIT = "academic_merit"
    NEED_BASED = "need_based"
    ATHLETIC = "athletic"
    STEM = "stem"
    ARTS = "arts"
    DIVERSITY = "diversity"
    FIRST_GENERATION = "first_generation"
    COMMUNITY_SERVICE = "community_service"
    LEADERSHIP = "leadership"
    LOCAL_COMMUNITY = "local_community"
    EMPLOYER_SPONSORED = "employer_sponsored"
    MILITARY = "military"
    RELIGIOUS = "religious"
    CAREER_SPECIFIC = "career_specific"
    ESSAY_BASED = "essay_based"
    RENEWABLE = "renewable"


class ScholarshipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"


# ===========================
# CORE SCHEMAS
# ===========================


class ScholarshipBase(BaseModel):
    """Base scholarship schema with common fields"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    organization: str = Field(..., min_length=1, max_length=255)
    website_url: Optional[str] = None
    application_url: Optional[str] = None

    # Classification
    scholarship_type: ScholarshipType
    categories: Optional[List[str]] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.MODERATE

    # Financial info
    amount_min: Optional[int] = Field(None, ge=0)
    amount_max: Optional[int] = Field(None, ge=0)
    amount_exact: Optional[int] = Field(None, ge=0)
    is_renewable: bool = False
    renewal_years: Optional[int] = Field(None, ge=1, le=10)
    number_of_awards: Optional[int] = Field(None, ge=1)

    # Academic requirements
    min_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    max_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    min_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    min_act_score: Optional[int] = Field(None, ge=1, le=36)
    required_majors: Optional[List[str]] = None
    excluded_majors: Optional[List[str]] = None
    academic_level: Optional[List[str]] = None

    # Demographics
    eligible_ethnicities: Optional[List[str]] = None
    gender_requirements: Optional[List[str]] = None
    first_generation_college_required: Optional[bool] = None

    # Financial need
    income_max: Optional[int] = Field(None, ge=0)
    income_min: Optional[int] = Field(None, ge=0)
    need_based_required: bool = False

    # Geographic
    eligible_states: Optional[List[str]] = None
    eligible_cities: Optional[List[str]] = None
    eligible_counties: Optional[List[str]] = None
    zip_codes: Optional[List[str]] = None
    international_students_eligible: bool = False

    # School requirements
    eligible_schools: Optional[List[str]] = None
    high_school_names: Optional[List[str]] = None
    graduation_year_min: Optional[int] = None
    graduation_year_max: Optional[int] = None

    # Activities
    required_activities: Optional[List[str]] = None
    volunteer_hours_min: Optional[int] = Field(None, ge=0)
    leadership_required: bool = False
    work_experience_required: bool = False
    special_talents: Optional[List[str]] = None

    # Application requirements
    essay_required: bool = False
    essay_topics: Optional[List[str]] = None
    essay_word_limit: Optional[int] = Field(None, ge=0)
    transcript_required: bool = True
    recommendation_letters_required: int = Field(0, ge=0, le=10)
    portfolio_required: bool = False
    interview_required: bool = False

    personal_statement_required: bool = False
    leadership_essay_required: bool = False
    community_service_essay_required: bool = False

    # Dates
    application_opens: Optional[datetime] = None
    deadline: Optional[datetime] = None
    award_date: Optional[datetime] = None
    is_rolling_deadline: bool = False

    # Additional
    languages_preferred: Optional[List[str]] = None
    military_affiliation_required: bool = False
    employer_affiliation: Optional[str] = None

    # Image fields (for scholarship cards)
    primary_image_url: Optional[str] = Field(None, max_length=500)
    primary_image_quality_score: Optional[int] = Field(None, ge=0, le=100)
    logo_image_url: Optional[str] = Field(None, max_length=500)

    @validator("amount_max")
    def validate_amount_range(cls, v, values):
        if (
            v
            and "amount_min" in values
            and values["amount_min"]
            and v < values["amount_min"]
        ):
            raise ValueError("amount_max must be greater than or equal to amount_min")
        return v

    @validator("max_gpa")
    def validate_gpa_range(cls, v, values):
        if v and "min_gpa" in values and values["min_gpa"] and v < values["min_gpa"]:
            raise ValueError("max_gpa must be greater than or equal to min_gpa")
        return v


class ScholarshipCreate(ScholarshipBase):
    """Schema for creating scholarships"""

    class Config:
        json_schema_extra = {
            "example": {
                "title": "National Merit Academic Excellence Scholarship",
                "description": "This scholarship recognizes outstanding academic achievement and leadership potential among high school seniors pursuing STEM fields.",
                "organization": "National Merit Foundation",
                "website_url": "https://www.nationalmerit.org",
                "application_url": "https://www.nationalmerit.org/apply",
                "scholarship_type": "academic_merit",
                "categories": ["STEM", "Leadership", "Academic Excellence"],
                "difficulty_level": "hard",
                "amount_min": 5000,
                "amount_max": 10000,
                "is_renewable": True,
                "renewal_years": 4,
                "number_of_awards": 50,
                "min_gpa": 3.8,
                "min_sat_score": 1450,
                "min_act_score": 32,
                "required_majors": ["Computer Science", "Engineering", "Mathematics"],
                "academic_level": ["undergraduate"],
                "eligible_states": ["California", "Texas", "Florida", "New York"],
                "graduation_year_min": 2025,
                "graduation_year_max": 2026,
                "required_activities": ["Science Fair Participation", "Math Club"],
                "volunteer_hours_min": 50,
                "leadership_required": True,
                "essay_required": True,
                "essay_topics": [
                    "How will your STEM education contribute to solving global challenges?"
                ],
                "essay_word_limit": 750,
                "transcript_required": True,
                "recommendation_letters_required": 3,
                "interview_required": True,
                "personal_statement_required": True,
                "leadership_essay_required": True,
                "deadline": "2025-03-15T23:59:59Z",
                "is_rolling_deadline": False,
                "primary_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/scholarships/national-merit.jpg",
                "primary_image_quality_score": 95,
                "logo_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/logos/national-merit-foundation.jpg",
            }
        }


class ScholarshipResponse(ScholarshipBase):
    """Schema for scholarship API responses"""

    id: int
    status: ScholarshipStatus
    verified: bool
    featured: bool
    views_count: int
    applications_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===========================
# SEARCH FILTERS
# ===========================


class ScholarshipSearchFilter(BaseModel):
    """Schema for scholarship search and filtering"""

    # Pagination
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    # Basic filters
    scholarship_type: Optional[str] = None
    active_only: bool = True
    verified_only: bool = False

    # Search terms
    search_query: Optional[str] = None

    # Financial filters
    min_amount: Optional[int] = Field(None, ge=0)
    max_amount: Optional[int] = Field(None, ge=0)

    # Academic filters
    student_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    student_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    student_act_score: Optional[int] = Field(None, ge=1, le=36)
    student_major: Optional[str] = None
    student_state: Optional[str] = None

    # Application requirement filters
    requires_essay: Optional[bool] = None

    # Deadline filters
    deadline_after: Optional[str] = None

    # Sorting
    sort_by: str = Field("created_at", pattern="^(deadline|amount|created_at|title)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


# ===========================
# BULK OPERATIONS
# ===========================


class BulkScholarshipCreate(BaseModel):
    """Schema for bulk scholarship creation"""

    scholarships: List[ScholarshipCreate]

    @validator("scholarships")
    def validate_scholarships_list(cls, v):
        if len(v) == 0:
            raise ValueError("At least one scholarship is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 scholarships per batch")
        return v
