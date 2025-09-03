# app/schemas/college.py - COMPLETE FILE
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.college import CollegeType, CollegeSize, AdmissionDifficulty
from enum import Enum
from pydantic import field_validator


class CollegeTypeEnum(str, Enum):
    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"
    COMMUNITY_COLLEGE = "community_college"


class CollegeSizeEnum(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class AdmissionDifficultyEnum(str, Enum):
    MOST_DIFFICULT = "most_difficult"
    VERY_DIFFICULT = "very_difficult"
    MODERATELY_DIFFICULT = "moderately_difficult"
    MINIMALLY_DIFFICULT = "minimally_difficult"
    NONCOMPETITIVE = "noncompetitive"


# ==========================================
# BASE SCHEMAS
# ==========================================


class CollegeBase(BaseModel):
    """Base college schema with core fields"""

    name: str = Field(..., min_length=1, max_length=255)
    short_name: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None

    # Location
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    region: Optional[str] = Field(None, max_length=50)

    # Institution Type
    college_type: CollegeTypeEnum
    is_historically_black: bool = False
    is_hispanic_serving: bool = False
    is_tribal_college: bool = False
    is_women_only: bool = False
    is_men_only: bool = False


# ==========================================
# SEARCH AND FILTER SCHEMAS
# ==========================================


class CollegeSearchFilter(BaseModel):
    """Schema for college search and filtering"""

    # Pagination
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    # Basic filters
    active_only: bool = True
    verified_only: bool = False

    # Search
    search_query: Optional[str] = None

    # Location
    state: Optional[str] = None
    region: Optional[str] = None
    campus_setting: Optional[str] = None

    # Institution type
    college_type: Optional[CollegeTypeEnum] = None
    college_size: Optional[CollegeSizeEnum] = None

    # Academic filters
    min_acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    admission_difficulty: Optional[AdmissionDifficultyEnum] = None

    # Student profile matching
    student_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    student_sat_score: Optional[int] = Field(None, ge=400, le=1600)
    student_act_score: Optional[int] = Field(None, ge=1, le=36)
    student_major: Optional[str] = None
    student_state: Optional[str] = None

    # Financial filters
    max_tuition_in_state: Optional[int] = Field(None, ge=0)
    max_tuition_out_of_state: Optional[int] = Field(None, ge=0)
    max_total_cost: Optional[int] = Field(None, ge=0)

    # Program filters
    required_majors: Optional[List[str]] = None
    strong_programs_only: Optional[bool] = None

    # Size filters
    min_enrollment: Optional[int] = Field(None, ge=0)
    max_enrollment: Optional[int] = Field(None, ge=0)

    # Diversity filters
    historically_black: Optional[bool] = None
    hispanic_serving: Optional[bool] = None
    tribal_college: Optional[bool] = None
    women_only: Optional[bool] = None
    men_only: Optional[bool] = None

    # Athletics
    athletic_division: Optional[str] = None

    # Outcomes
    min_graduation_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    min_retention_rate: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Sorting
    sort_by: str = "name"
    sort_order: str = Field("asc", regex="^(asc|desc)$")

    sort_order: str = "asc"

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v


# ==========================================
# CRUD SCHEMAS
# ==========================================


class CollegeCreate(CollegeBase):
    """Schema for creating a new college"""

    # Size and Demographics
    total_enrollment: Optional[int] = Field(None, ge=0)
    undergraduate_enrollment: Optional[int] = Field(None, ge=0)
    graduate_enrollment: Optional[int] = Field(None, ge=0)
    college_size: Optional[CollegeSizeEnum] = None

    # Academic Information
    acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    admission_difficulty: Optional[AdmissionDifficultyEnum] = None

    # Test Score Ranges
    sat_math_25: Optional[int] = Field(None, ge=200, le=800)
    sat_math_75: Optional[int] = Field(None, ge=200, le=800)
    sat_reading_25: Optional[int] = Field(None, ge=200, le=800)
    sat_reading_75: Optional[int] = Field(None, ge=200, le=800)
    sat_total_25: Optional[int] = Field(None, ge=400, le=1600)
    sat_total_75: Optional[int] = Field(None, ge=400, le=1600)

    act_composite_25: Optional[int] = Field(None, ge=1, le=36)
    act_composite_75: Optional[int] = Field(None, ge=1, le=36)

    # GPA Requirements
    avg_gpa: Optional[float] = Field(None, ge=0.0, le=5.0)
    min_gpa_recommended: Optional[float] = Field(None, ge=0.0, le=5.0)

    # Financial Information
    tuition_in_state: Optional[int] = Field(None, ge=0)
    tuition_out_of_state: Optional[int] = Field(None, ge=0)
    room_and_board: Optional[int] = Field(None, ge=0)
    total_cost_in_state: Optional[int] = Field(None, ge=0)
    total_cost_out_of_state: Optional[int] = Field(None, ge=0)

    # Financial Aid
    avg_financial_aid: Optional[int] = Field(None, ge=0)
    percent_receiving_aid: Optional[float] = Field(None, ge=0.0, le=1.0)
    avg_net_price: Optional[int] = Field(None, ge=0)

    # Academic Programs
    available_majors: Optional[List[str]] = None
    popular_majors: Optional[List[str]] = None
    strong_programs: Optional[List[str]] = None

    # Campus Life
    campus_setting: Optional[str] = Field(None, max_length=50)
    housing_guaranteed: bool = False
    greek_life_available: bool = False

    # Athletics
    athletic_division: Optional[str] = Field(None, max_length=20)
    athletic_conferences: Optional[List[str]] = None

    # Rankings and Recognition
    us_news_ranking: Optional[int] = Field(None, ge=1)
    forbes_ranking: Optional[int] = Field(None, ge=1)
    other_rankings: Optional[Dict[str, Any]] = None

    # Outcomes
    graduation_rate_4_year: Optional[float] = Field(None, ge=0.0, le=1.0)
    graduation_rate_6_year: Optional[float] = Field(None, ge=0.0, le=1.0)
    retention_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    employment_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    avg_starting_salary: Optional[int] = Field(None, ge=0)

    # Diversity
    percent_white: Optional[float] = Field(None, ge=0.0, le=1.0)
    percent_black: Optional[float] = Field(None, ge=0.0, le=1.0)
    percent_hispanic: Optional[float] = Field(None, ge=0.0, le=1.0)
    percent_asian: Optional[float] = Field(None, ge=0.0, le=1.0)
    percent_international: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Application Information
    application_deadline: Optional[str] = Field(None, max_length=50)
    early_decision_deadline: Optional[str] = Field(None, max_length=50)
    early_action_deadline: Optional[str] = Field(None, max_length=50)
    application_fee: Optional[int] = Field(None, ge=0)
    common_app_accepted: bool = False

    # Requirements
    essays_required: bool = False
    letters_of_recommendation: Optional[int] = Field(None, ge=0)
    interview_required: bool = False

    # Status
    is_active: bool = True
    is_verified: bool = False
    data_source: Optional[str] = Field(None, max_length=100)

    @validator("sat_total_25", "sat_total_75")
    def validate_sat_total(cls, v, values):
        """Validate SAT total scores"""
        if v is not None:
            sat_math_25 = values.get("sat_math_25")
            sat_reading_25 = values.get("sat_reading_25")
            if sat_math_25 and sat_reading_25:
                expected_min = sat_math_25 + sat_reading_25
                if v < expected_min - 50:  # Allow some flexibility
                    raise ValueError(
                        "SAT total should approximately equal math + reading scores"
                    )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "University of New Hampshire",
                "short_name": "UNH",
                "website": "https://www.unh.edu",
                "city": "Durham",
                "state": "New Hampshire",
                "zip_code": "03824",
                "region": "Northeast",
                "college_type": "public",
                "total_enrollment": 15000,
                "college_size": "medium",
                "acceptance_rate": 0.78,
                "admission_difficulty": "moderately_difficult",
                "sat_total_25": 1150,
                "sat_total_75": 1310,
                "avg_gpa": 3.5,
                "tuition_in_state": 18499,
                "tuition_out_of_state": 35077,
                "available_majors": ["Business", "Engineering", "Liberal Arts"],
                "campus_setting": "Suburban",
                "athletic_division": "D1",
            }
        }


class CollegeUpdate(BaseModel):
    """Schema for updating college information"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    short_name: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None

    # Location
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    region: Optional[str] = Field(None, max_length=50)

    # Institution Type
    college_type: Optional[CollegeTypeEnum] = None
    is_historically_black: Optional[bool] = None
    is_hispanic_serving: Optional[bool] = None
    is_tribal_college: Optional[bool] = None
    is_women_only: Optional[bool] = None
    is_men_only: Optional[bool] = None

    # Academic and financial fields (all optional for updates)
    total_enrollment: Optional[int] = Field(None, ge=0)
    acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    tuition_in_state: Optional[int] = Field(None, ge=0)
    tuition_out_of_state: Optional[int] = Field(None, ge=0)
    available_majors: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class CollegeResponse(CollegeBase):
    """Schema for college API responses"""

    id: int

    # Size and Demographics
    total_enrollment: Optional[int] = None
    undergraduate_enrollment: Optional[int] = None
    graduate_enrollment: Optional[int] = None
    college_size: Optional[CollegeSizeEnum] = None

    # Academic Information
    acceptance_rate: Optional[float] = None
    admission_difficulty: Optional[AdmissionDifficultyEnum] = None

    # Test Score Ranges
    sat_total_25: Optional[int] = None
    sat_total_75: Optional[int] = None
    act_composite_25: Optional[int] = None
    act_composite_75: Optional[int] = None

    # GPA Requirements
    avg_gpa: Optional[float] = None
    min_gpa_recommended: Optional[float] = None

    # Financial Information
    tuition_in_state: Optional[int] = None
    tuition_out_of_state: Optional[int] = None
    room_and_board: Optional[int] = None
    total_cost_in_state: Optional[int] = None
    total_cost_out_of_state: Optional[int] = None

    # Financial Aid
    avg_financial_aid: Optional[int] = None
    percent_receiving_aid: Optional[float] = None
    avg_net_price: Optional[int] = None

    # Academic Programs
    available_majors: Optional[List[str]] = None
    popular_majors: Optional[List[str]] = None
    strong_programs: Optional[List[str]] = None

    # Campus Life
    campus_setting: Optional[str] = None
    housing_guaranteed: Optional[bool] = None
    greek_life_available: Optional[bool] = None

    # Athletics
    athletic_division: Optional[str] = None
    athletic_conferences: Optional[List[str]] = None

    # Rankings
    us_news_ranking: Optional[int] = None
    forbes_ranking: Optional[int] = None
    other_rankings: Optional[Dict[str, Any]] = None

    # Outcomes
    graduation_rate_4_year: Optional[float] = None
    graduation_rate_6_year: Optional[float] = None
    retention_rate: Optional[float] = None
    employment_rate: Optional[float] = None
    avg_starting_salary: Optional[int] = None

    # Diversity
    percent_white: Optional[float] = None
    percent_black: Optional[float] = None
    percent_hispanic: Optional[float] = None
    percent_asian: Optional[float] = None
    percent_international: Optional[float] = None

    # Application Information
    application_deadline: Optional[str] = None
    early_decision_deadline: Optional[str] = None
    early_action_deadline: Optional[str] = None
    application_fee: Optional[int] = None
    common_app_accepted: Optional[bool] = None

    # Requirements
    essays_required: Optional[bool] = None
    letters_of_recommendation: Optional[int] = None
    interview_required: Optional[bool] = None

    # Status
    is_active: bool
    is_verified: bool
    data_source: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# COLLEGE MATCH SCHEMAS
# ==========================================


class CollegeMatchCreate(BaseModel):
    """Schema for creating college matches"""

    user_id: int
    college_id: int
    match_score: float = Field(..., ge=0.0, le=100.0)
    match_category: Optional[str] = Field(None, regex="^(safety|match|reach)$")
    match_reasons: Optional[List[str]] = None
    concerns: Optional[List[str]] = None


class CollegeMatchUpdate(BaseModel):
    """Schema for updating college match status"""

    viewed: Optional[bool] = None
    interested: Optional[bool] = None
    applied: Optional[bool] = None
    bookmarked: Optional[bool] = None
    application_status: Optional[str] = None
    application_deadline: Optional[datetime] = None
    user_notes: Optional[str] = None


class CollegeMatchResponse(BaseModel):
    """Schema for college match responses"""

    id: int
    user_id: int
    college_id: int
    college: CollegeResponse

    # Match scoring
    match_score: float
    match_category: Optional[str] = None
    match_reasons: Optional[List[str]] = None
    concerns: Optional[List[str]] = None

    # User interaction
    viewed: bool
    interested: Optional[bool] = None
    applied: bool
    bookmarked: bool

    # Application status
    application_status: Optional[str] = None
    application_deadline: Optional[datetime] = None
    user_notes: Optional[str] = None

    # Timestamps
    match_date: datetime
    viewed_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CollegeMatchSummary(BaseModel):
    """Summary of college matches for a user"""

    user_id: int
    total_matches: int
    safety_schools: int
    match_schools: int
    reach_schools: int
    viewed_count: int
    applied_count: int
    bookmarked_count: int
    interested_count: int
    average_match_score: float
    best_match_score: float
    matches_this_month: int
    upcoming_deadlines: int

    # Financial summary
    avg_cost_in_state: Optional[int] = None
    avg_cost_out_of_state: Optional[int] = None
    most_affordable_match: Optional[str] = None

    # Academic summary
    avg_acceptance_rate: Optional[float] = None
    most_competitive_match: Optional[str] = None


# ==========================================
# BATCH AND UTILITY SCHEMAS
# ==========================================


class CollegeBatchCreate(BaseModel):
    """Schema for batch creating colleges"""

    colleges: List[CollegeCreate] = Field(..., min_items=1, max_items=100)


class CollegeBatchResponse(BaseModel):
    """Response for batch college creation"""

    success_count: int
    error_count: int
    errors: Optional[List[str]] = None
    created_ids: Optional[List[int]] = None


class CollegeStatistics(BaseModel):
    """College platform statistics"""

    total_colleges: int
    active_colleges: int
    verified_colleges: int
    colleges_by_type: Dict[str, int]
    colleges_by_size: Dict[str, int]
    colleges_by_state: Dict[str, int]
    avg_acceptance_rate: Optional[float] = None
    avg_tuition_public: Optional[int] = None
    avg_tuition_private: Optional[int] = None


# ==========================================
# RECOMMENDATION SCHEMAS
# ==========================================


class CollegeRecommendationRequest(BaseModel):
    """Request for college recommendations"""

    user_id: Optional[int] = None  # Use current user if not provided
    limit: int = Field(20, ge=1, le=100)
    include_safety: bool = True
    include_match: bool = True
    include_reach: bool = True
    force_recalculate: bool = False


class CollegeRecommendationResponse(BaseModel):
    """Response for college recommendations"""

    recommendations: List[CollegeMatchResponse]
    summary: CollegeMatchSummary
    total_colleges_analyzed: int
    recommendation_generated_at: datetime
