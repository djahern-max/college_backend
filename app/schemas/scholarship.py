# app/schemas/scholarship.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.scholarship import ScholarshipStatus, ScholarshipType


class ScholarshipBase(BaseModel):
    """Base scholarship schema with common fields"""

    # Basic Information
    title: str = Field(..., min_length=1, max_length=500)
    provider: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    # Financial Information
    amount_min: Optional[float] = Field(None, ge=0)
    amount_max: Optional[float] = Field(None, ge=0)
    amount_exact: Optional[float] = Field(None, ge=0)
    renewable: bool = False
    renewable_years: Optional[int] = Field(None, ge=1, le=10)

    # Application Information
    deadline: Optional[datetime] = None
    application_url: Optional[str] = Field(None, max_length=1000)
    contact_email: Optional[str] = Field(None, max_length=255)
    application_fee: float = Field(0.0, ge=0)

    # Status and Verification
    status: ScholarshipStatus = ScholarshipStatus.ACTIVE
    verified: bool = False

    # Categorization
    scholarship_type: ScholarshipType
    categories: Optional[List[str]] = None

    # Academic Requirements
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    max_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    min_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    min_act_score: Optional[int] = Field(None, ge=1, le=36)
    required_majors: Optional[List[str]] = None
    academic_interests: Optional[List[str]] = None

    # Geographic Requirements
    eligible_states: Optional[List[str]] = None
    eligible_cities: Optional[List[str]] = None
    zip_codes: Optional[List[str]] = None

    # Demographic Requirements
    eligible_ethnicities: Optional[List[str]] = None
    first_generation_college_required: Optional[bool] = None
    income_max: Optional[float] = Field(None, ge=0)
    income_min: Optional[float] = Field(None, ge=0)

    # High School Requirements
    high_school_names: Optional[List[str]] = None
    graduation_year_min: Optional[int] = None
    graduation_year_max: Optional[int] = None

    # Activity Requirements
    required_activities: Optional[List[str]] = None
    volunteer_hours_min: Optional[int] = Field(None, ge=0)
    leadership_required: bool = False

    # Essay Requirements
    essay_required: bool = False
    personal_statement_required: bool = False
    leadership_essay_required: bool = False

    # Additional Requirements
    languages_preferred: Optional[List[str]] = None
    special_talents: Optional[List[str]] = None
    college_size_preference: Optional[List[str]] = None
    college_location_preference: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None
    additional_requirements: Optional[Dict[str, Any]] = None

    # Source Information
    source_url: Optional[str] = Field(None, max_length=1000)
    data_source: Optional[str] = Field(None, max_length=100)
    external_id: Optional[str] = Field(None, max_length=255)

    # Admin Information
    notes: Optional[str] = None

    @validator("amount_max")
    def validate_amount_range(cls, v, values):
        if (
            v is not None
            and "amount_min" in values
            and values["amount_min"] is not None
        ):
            if v < values["amount_min"]:
                raise ValueError(
                    "amount_max must be greater than or equal to amount_min"
                )
        return v

    @validator("max_gpa")
    def validate_gpa_range(cls, v, values):
        if v is not None and "min_gpa" in values and values["min_gpa"] is not None:
            if v < values["min_gpa"]:
                raise ValueError("max_gpa must be greater than or equal to min_gpa")
        return v

    @validator("graduation_year_max")
    def validate_graduation_year_range(cls, v, values):
        if (
            v is not None
            and "graduation_year_min" in values
            and values["graduation_year_min"] is not None
        ):
            if v < values["graduation_year_min"]:
                raise ValueError(
                    "graduation_year_max must be greater than or equal to graduation_year_min"
                )
        return v

    @validator("income_max")
    def validate_income_range(cls, v, values):
        if (
            v is not None
            and "income_min" in values
            and values["income_min"] is not None
        ):
            if v < values["income_min"]:
                raise ValueError(
                    "income_max must be greater than or equal to income_min"
                )
        return v


class ScholarshipCreate(ScholarshipBase):
    """Schema for creating new scholarships"""

    pass


class ScholarshipUpdate(BaseModel):
    """Schema for updating existing scholarships (all fields optional)"""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    amount_min: Optional[float] = Field(None, ge=0)
    amount_max: Optional[float] = Field(None, ge=0)
    amount_exact: Optional[float] = Field(None, ge=0)
    renewable: Optional[bool] = None
    renewable_years: Optional[int] = Field(None, ge=1, le=10)
    deadline: Optional[datetime] = None
    application_url: Optional[str] = Field(None, max_length=1000)
    contact_email: Optional[str] = Field(None, max_length=255)
    application_fee: Optional[float] = Field(None, ge=0)
    status: Optional[ScholarshipStatus] = None
    verified: Optional[bool] = None
    scholarship_type: Optional[ScholarshipType] = None
    categories: Optional[List[str]] = None

    # All other fields as optional...
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    max_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    min_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    min_act_score: Optional[int] = Field(None, ge=1, le=36)
    required_majors: Optional[List[str]] = None
    academic_interests: Optional[List[str]] = None
    eligible_states: Optional[List[str]] = None
    eligible_cities: Optional[List[str]] = None
    zip_codes: Optional[List[str]] = None
    eligible_ethnicities: Optional[List[str]] = None
    first_generation_college_required: Optional[bool] = None
    income_max: Optional[float] = Field(None, ge=0)
    income_min: Optional[float] = Field(None, ge=0)
    high_school_names: Optional[List[str]] = None
    graduation_year_min: Optional[int] = None
    graduation_year_max: Optional[int] = None
    required_activities: Optional[List[str]] = None
    volunteer_hours_min: Optional[int] = Field(None, ge=0)
    leadership_required: Optional[bool] = None
    essay_required: Optional[bool] = None
    personal_statement_required: Optional[bool] = None
    leadership_essay_required: Optional[bool] = None
    languages_preferred: Optional[List[str]] = None
    special_talents: Optional[List[str]] = None
    college_size_preference: Optional[List[str]] = None
    college_location_preference: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None
    additional_requirements: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = Field(None, max_length=1000)
    data_source: Optional[str] = Field(None, max_length=100)
    external_id: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class ScholarshipResponse(ScholarshipBase):
    """Schema for scholarship API responses"""

    id: int
    view_count: int
    application_count: int
    match_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    deadline_reminder_sent: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "STEM Excellence Scholarship",
                "provider": "Tech Foundation",
                "description": "Supporting students pursuing STEM degrees",
                "amount_min": 5000,
                "amount_max": 10000,
                "renewable": True,
                "renewable_years": 4,
                "deadline": "2025-03-15T23:59:59Z",
                "scholarship_type": "stem",
                "min_gpa": 3.5,
                "min_sat_score": 1200,
                "required_majors": ["Computer Science", "Engineering", "Mathematics"],
                "verified": True,
                "created_at": "2025-01-01T10:00:00Z",
            }
        }


class ScholarshipMatchCreate(BaseModel):
    """Schema for creating scholarship matches"""

    user_id: int
    scholarship_id: int
    match_score: float = Field(..., ge=0, le=100)
    match_reasons: Optional[List[str]] = None
    mismatch_reasons: Optional[List[str]] = None


class ScholarshipMatchUpdate(BaseModel):
    """Schema for updating scholarship match status"""

    viewed: Optional[bool] = None
    interested: Optional[bool] = None
    applied: Optional[bool] = None
    bookmarked: Optional[bool] = None


class ScholarshipMatchResponse(BaseModel):
    """Schema for scholarship match responses"""

    id: int
    user_id: int
    scholarship_id: int
    match_score: float
    match_reasons: Optional[List[str]]
    mismatch_reasons: Optional[List[str]]
    viewed: bool
    interested: Optional[bool]
    applied: bool
    bookmarked: bool
    match_date: datetime
    viewed_at: Optional[datetime]
    applied_at: Optional[datetime]

    # Include scholarship details for convenience
    scholarship: ScholarshipResponse

    class Config:
        from_attributes = True


class ScholarshipSearchFilter(BaseModel):
    """Schema for scholarship search filters"""

    # Basic filters
    scholarship_type: Optional[ScholarshipType] = None
    verified_only: bool = True
    active_only: bool = True

    # Amount filters
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)

    # Academic filters
    student_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    student_sat: Optional[int] = Field(None, ge=400, le=1600)
    student_act: Optional[int] = Field(None, ge=1, le=36)
    student_major: Optional[str] = None

    # Geographic filters
    student_state: Optional[str] = None
    student_city: Optional[str] = None
    student_zip: Optional[str] = None

    # Demographic filters
    student_ethnicity: Optional[List[str]] = None
    is_first_generation: Optional[bool] = None
    household_income: Optional[float] = Field(None, ge=0)

    # Other filters
    requires_essay: Optional[bool] = None
    requires_leadership: Optional[bool] = None
    deadline_after: Optional[datetime] = None
    deadline_before: Optional[datetime] = None

    # Pagination
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=100)

    # Sorting
    sort_by: str = Field(
        "match_score", pattern="^(match_score|deadline|amount|created_at|title)$"
    )
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class ScholarshipMatchSummary(BaseModel):
    """Schema for user's scholarship match summary"""

    user_id: int
    total_matches: int
    high_matches: int  # Matches with score >= 80
    medium_matches: int  # Matches with score 60-79
    low_matches: int  # Matches with score < 60
    viewed_count: int
    applied_count: int
    bookmarked_count: int
    interested_count: int
    average_match_score: float
    best_match_score: float
    matches_this_month: int
    upcoming_deadlines: int  # Deadlines in next 30 days

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "total_matches": 45,
                "high_matches": 12,
                "medium_matches": 23,
                "low_matches": 10,
                "viewed_count": 18,
                "applied_count": 5,
                "bookmarked_count": 8,
                "interested_count": 15,
                "average_match_score": 72.5,
                "best_match_score": 95.0,
                "matches_this_month": 12,
                "upcoming_deadlines": 6,
            }
        }
