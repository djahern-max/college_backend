# app/schemas/scholarship.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Import enums from model
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
# BASE SCHEMAS
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


# ===========================
# CRUD SCHEMAS
# ===========================


# Replace the existing json_schema_extra in your ScholarshipCreate class
# in app/schemas/scholarship.py


class ScholarshipCreate(ScholarshipBase):
    """Schema for creating scholarships"""

    pass

    class Config:
        json_schema_extra = {
            "example": {
                # ===========================
                # BASIC INFORMATION
                # ===========================
                "title": "Future Leaders in Technology Scholarship",
                "description": "Supporting exceptional students pursuing STEM degrees who demonstrate leadership potential, academic excellence, and commitment to using technology for positive social impact. Recipients receive mentorship, internship opportunities, and networking access.",
                "organization": "Tech Innovation Foundation",
                "website_url": "https://techinnovation.org/scholarships",
                "application_url": "https://apply.techinnovation.org/future-leaders",
                # ===========================
                # CLASSIFICATION
                # ===========================
                "scholarship_type": "stem",
                "categories": [
                    "Computer Science",
                    "Software Engineering",
                    "Data Science",
                    "Cybersecurity",
                ],
                "difficulty_level": "hard",
                # ===========================
                # FINANCIAL INFORMATION
                # ===========================
                "amount_min": 7500,
                "amount_max": 15000,
                "is_renewable": True,
                "renewal_years": 4,
                "number_of_awards": 25,
                # ===========================
                # ACADEMIC REQUIREMENTS
                # ===========================
                "min_gpa": 3.7,
                "min_sat_score": 1450,
                "min_act_score": 33,
                "required_majors": [
                    "Computer Science",
                    "Software Engineering",
                    "Data Science",
                    "Information Technology",
                    "Computer Engineering",
                ],
                "academic_level": ["undergraduate"],
                # ===========================
                # DEMOGRAPHIC REQUIREMENTS
                # ===========================
                "eligible_ethnicities": [
                    "African American",
                    "Hispanic/Latino",
                    "Native American",
                ],
                "first_generation_college_required": None,
                # ===========================
                # FINANCIAL NEED
                # ===========================
                "income_max": 100000,
                "need_based_required": True,
                # ===========================
                # GEOGRAPHIC REQUIREMENTS
                # ===========================
                "eligible_states": ["CA", "NY", "TX", "FL", "WA", "IL", "PA"],
                "eligible_cities": [
                    "San Francisco",
                    "New York",
                    "Austin",
                    "Seattle",
                    "Boston",
                ],
                "international_students_eligible": False,
                # ===========================
                # EDUCATION REQUIREMENTS
                # ===========================
                "graduation_year_min": 2025,
                "graduation_year_max": 2027,
                # ===========================
                # ACTIVITY REQUIREMENTS
                # ===========================
                "required_activities": [
                    "STEM Club Participation",
                    "Programming Projects",
                    "Technology Leadership",
                    "Community Tech Volunteer Work",
                ],
                "volunteer_hours_min": 40,
                "leadership_required": True,
                "special_talents": [
                    "Programming",
                    "Web Development",
                    "Mobile App Development",
                    "Data Analysis",
                    "Machine Learning",
                ],
                # ===========================
                # APPLICATION REQUIREMENTS
                # ===========================
                "essay_required": True,
                "essay_topics": [
                    "How will you use technology to solve a real-world problem?",
                    "Describe a coding project that demonstrates your skills",
                    "What does diversity in technology mean to you?",
                ],
                "essay_word_limit": 750,
                "transcript_required": True,
                "recommendation_letters_required": 3,
                "portfolio_required": True,
                "interview_required": True,
                "personal_statement_required": True,
                "leadership_essay_required": True,
                "community_service_essay_required": False,
                # ===========================
                # DATES & DEADLINES
                # ===========================
                "application_opens": "2024-10-01T00:00:00Z",
                "deadline": "2025-02-15T23:59:59Z",
                "award_date": "2025-04-15T00:00:00Z",
                "is_rolling_deadline": False,
                # ===========================
                # ADDITIONAL PREFERENCES
                # ===========================
                "languages_preferred": ["Python", "JavaScript", "Java", "Spanish"],
                "military_affiliation_required": False,
                "employer_affiliation": "Must commit to 2-year mentorship program with partner tech companies",
            }
        }


class ScholarshipUpdate(BaseModel):
    """Schema for updating scholarships - all fields optional"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    organization: Optional[str] = Field(None, min_length=1, max_length=255)
    website_url: Optional[str] = None
    application_url: Optional[str] = None

    scholarship_type: Optional[ScholarshipType] = None
    categories: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ScholarshipStatus] = None

    # Financial
    amount_min: Optional[int] = Field(None, ge=0)
    amount_max: Optional[int] = Field(None, ge=0)
    amount_exact: Optional[int] = Field(None, ge=0)
    is_renewable: Optional[bool] = None

    # Academic
    min_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    min_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    min_act_score: Optional[int] = Field(None, ge=1, le=36)
    required_majors: Optional[List[str]] = None

    # Other fields can be added as needed for updates
    deadline: Optional[datetime] = None


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
# MATCHING SCHEMAS
# ===========================


class ScholarshipMatchCreate(BaseModel):
    """Schema for creating scholarship matches"""

    user_id: int
    scholarship_id: int
    match_score: float = Field(..., ge=0.0, le=100.0)
    match_reasons: Optional[List[str]] = None
    mismatch_reasons: Optional[List[str]] = None


class ScholarshipMatchUpdate(BaseModel):
    """Schema for updating user's scholarship match interaction"""

    viewed: Optional[bool] = None
    interested: Optional[bool] = None
    applied: Optional[bool] = None
    bookmarked: Optional[bool] = None
    application_status: Optional[str] = None
    notes: Optional[str] = None


class ScholarshipMatchResponse(BaseModel):
    """Schema for scholarship match responses"""

    id: int
    user_id: int
    scholarship_id: int
    match_score: float
    match_reasons: Optional[List[str]] = None
    mismatch_reasons: Optional[List[str]] = None

    # User interaction
    viewed: bool
    interested: Optional[bool] = None
    applied: bool
    bookmarked: bool
    application_status: Optional[str] = None
    notes: Optional[str] = None

    # Timestamps
    match_date: datetime
    viewed_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None

    # Related scholarship info
    scholarship: Optional[ScholarshipResponse] = None

    class Config:
        from_attributes = True


# ===========================
# SEARCH & FILTERING SCHEMAS
# ===========================


class ScholarshipSearchFilter(BaseModel):
    """Schema for scholarship search and filtering"""

    # Pagination
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    # Basic filters
    scholarship_type: Optional[ScholarshipType] = None
    active_only: bool = True
    verified_only: bool = False
    featured_only: bool = False

    # Search terms
    search_query: Optional[str] = None  # Search in title, description, organization
    organization: Optional[str] = None

    # Financial filters
    min_amount: Optional[int] = Field(None, ge=0)
    max_amount: Optional[int] = Field(None, ge=0)
    renewable_only: Optional[bool] = None

    # Academic filters
    student_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    student_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    student_act_score: Optional[int] = Field(None, ge=1, le=36)
    student_major: Optional[str] = None

    # Geographic filters
    student_state: Optional[str] = None
    student_city: Optional[str] = None

    # Demographic filters
    is_first_generation: Optional[bool] = None
    student_ethnicity: Optional[List[str]] = None
    # Application requirement filters
    requires_essay: Optional[bool] = None
    requires_leadership: Optional[bool] = None
    max_essay_requirements: Optional[int] = Field(None, ge=0, le=5)

    # Deadline filters
    deadline_after: Optional[datetime] = None
    deadline_before: Optional[datetime] = None
    rolling_deadline_only: Optional[bool] = None

    # Difficulty filter
    max_difficulty: Optional[DifficultyLevel] = None

    # Sorting
    sort_by: str = Field(
        "created_at", pattern="^(match_score|deadline|amount|created_at|title)$"
    )
    sort_order: str = Field("desc", pattern="^(asc|desc)$")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "limit": 20,
                "scholarship_type": "stem",
                "active_only": True,
                "verified_only": True,
                "min_amount": 1000,
                "student_gpa": 3.7,
                "student_sat_score": 1400,
                "student_major": "Computer Science",
                "student_state": "CA",
                "requires_essay": False,
                "deadline_after": "2025-01-01T00:00:00Z",
                "sort_by": "match_score",
                "sort_order": "desc",
            }
        }


# ===========================
# SUMMARY & ANALYTICS SCHEMAS
# ===========================


class ScholarshipMatchSummary(BaseModel):
    """Summary of user's scholarship matches"""

    user_id: int
    total_matches: int
    high_matches: int  # Score >= 80
    medium_matches: int  # Score 60-79
    low_matches: int  # Score < 60

    # User interaction stats
    viewed_count: int
    applied_count: int
    bookmarked_count: int
    interested_count: int

    # Score statistics
    average_match_score: float
    best_match_score: float

    # Time-based stats
    matches_this_month: int
    upcoming_deadlines: int  # Next 30 days

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "total_matches": 45,
                "high_matches": 12,
                "medium_matches": 23,
                "low_matches": 10,
                "viewed_count": 25,
                "applied_count": 8,
                "bookmarked_count": 15,
                "interested_count": 20,
                "average_match_score": 72.5,
                "best_match_score": 94.2,
                "matches_this_month": 8,
                "upcoming_deadlines": 5,
            }
        }


class ScholarshipStatistics(BaseModel):
    """Platform-wide scholarship statistics"""

    total_scholarships: int
    active_scholarships: int
    verified_scholarships: int
    total_amount_available: int
    scholarship_types: Dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "total_scholarships": 1250,
                "active_scholarships": 890,
                "verified_scholarships": 654,
                "total_amount_available": 15750000,
                "scholarship_types": {
                    "academic_merit": 234,
                    "stem": 156,
                    "need_based": 89,
                    "diversity": 78,
                    "community_service": 67,
                },
            }
        }


# ===========================
# BATCH OPERATIONS
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


class BulkMatchingRequest(BaseModel):
    """Schema for bulk matching operations"""

    user_ids: Optional[List[int]] = None  # If None, match all users
    scholarship_ids: Optional[List[int]] = None  # If None, match all scholarships
    force_recalculate: bool = False
    min_score_threshold: float = Field(30.0, ge=0.0, le=100.0)


class BulkMatchingResponse(BaseModel):
    """Response schema for bulk matching operations"""

    users_processed: int
    scholarships_processed: int
    matches_created: int
    matches_updated: int
    processing_time_seconds: float
    errors: List[str] = []


# ===========================
# ADMIN SCHEMAS
# ===========================


class ScholarshipVerificationUpdate(BaseModel):
    """Schema for admin scholarship verification"""

    verified: bool
    verification_notes: Optional[str] = None
    featured: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "verified": True,
                "verification_notes": "Verified with organization. All information accurate as of 2025-01-01.",
                "featured": False,
            }
        }
