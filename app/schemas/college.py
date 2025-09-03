# app/schemas/college.py - OPTIMIZED VERSION
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# ==========================================
# ENUMS (consistent with model)
# ==========================================


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


class MatchCategoryEnum(str, Enum):
    SAFETY = "safety"
    MATCH = "match"
    REACH = "reach"


class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"


# ==========================================
# BASE SCHEMAS
# ==========================================


class CollegeBase(BaseModel):
    """Base college schema with core required fields"""

    # Basic Information
    name: str = Field(..., min_length=1, max_length=255, description="College name")
    short_name: Optional[str] = Field(
        None, max_length=100, description="Short name or abbreviation"
    )
    website: Optional[str] = Field(None, description="College website URL")

    # Location (required)
    city: str = Field(..., min_length=1, max_length=100, description="City location")
    state: str = Field(..., min_length=2, max_length=50, description="State location")
    zip_code: Optional[str] = Field(None, max_length=10, description="ZIP code")
    region: Optional[str] = Field(None, max_length=50, description="Geographic region")

    # Institution Type (required)
    college_type: CollegeTypeEnum = Field(..., description="Type of institution")

    # Special designations
    is_historically_black: bool = Field(default=False, description="HBCU designation")
    is_hispanic_serving: bool = Field(default=False, description="HSI designation")
    is_tribal_college: bool = Field(
        default=False, description="Tribal college designation"
    )
    is_women_only: bool = Field(default=False, description="Women-only institution")
    is_men_only: bool = Field(default=False, description="Men-only institution")


# ==========================================
# CRUD SCHEMAS
# ==========================================


class CollegeCreate(CollegeBase):
    """Schema for creating a new college with comprehensive data"""

    # Size and Demographics
    total_enrollment: Optional[int] = Field(
        None, ge=0, description="Total student enrollment"
    )
    undergraduate_enrollment: Optional[int] = Field(
        None, ge=0, description="Undergraduate enrollment"
    )
    graduate_enrollment: Optional[int] = Field(
        None, ge=0, description="Graduate enrollment"
    )
    college_size: Optional[CollegeSizeEnum] = Field(
        None, description="College size category"
    )

    # Academic Information
    acceptance_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Acceptance rate (0-1)"
    )
    admission_difficulty: Optional[AdmissionDifficultyEnum] = Field(
        None, description="Admission difficulty level"
    )

    # Test Score Ranges (25th-75th percentile)
    sat_math_25: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Math 25th percentile"
    )
    sat_math_75: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Math 75th percentile"
    )
    sat_reading_25: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Reading 25th percentile"
    )
    sat_reading_75: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Reading 75th percentile"
    )
    sat_total_25: Optional[int] = Field(
        None, ge=400, le=1600, description="SAT Total 25th percentile"
    )
    sat_total_75: Optional[int] = Field(
        None, ge=400, le=1600, description="SAT Total 75th percentile"
    )

    act_composite_25: Optional[int] = Field(
        None, ge=1, le=36, description="ACT Composite 25th percentile"
    )
    act_composite_75: Optional[int] = Field(
        None, ge=1, le=36, description="ACT Composite 75th percentile"
    )

    # GPA Requirements
    avg_gpa: Optional[float] = Field(
        None, ge=0.0, le=5.0, description="Average GPA of admitted students"
    )
    min_gpa_recommended: Optional[float] = Field(
        None, ge=0.0, le=5.0, description="Minimum recommended GPA"
    )

    # Financial Information
    tuition_in_state: Optional[int] = Field(
        None, ge=0, description="In-state tuition cost"
    )
    tuition_out_of_state: Optional[int] = Field(
        None, ge=0, description="Out-of-state tuition cost"
    )
    room_and_board: Optional[int] = Field(None, ge=0, description="Room and board cost")
    total_cost_in_state: Optional[int] = Field(
        None, ge=0, description="Total in-state cost"
    )
    total_cost_out_of_state: Optional[int] = Field(
        None, ge=0, description="Total out-of-state cost"
    )

    # Financial Aid
    avg_financial_aid: Optional[int] = Field(
        None, ge=0, description="Average financial aid amount"
    )
    percent_receiving_aid: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percent receiving aid"
    )
    avg_net_price: Optional[int] = Field(
        None, ge=0, description="Average net price after aid"
    )

    # Academic Programs
    available_majors: Optional[List[str]] = Field(
        None, description="List of available majors"
    )
    popular_majors: Optional[List[str]] = Field(
        None, description="List of popular majors"
    )
    strong_programs: Optional[List[str]] = Field(
        None, description="List of nationally recognized programs"
    )

    # Campus Life
    campus_setting: Optional[str] = Field(
        None, max_length=50, description="Urban/Suburban/Rural"
    )
    housing_guaranteed: bool = Field(
        default=False, description="Housing guaranteed for students"
    )
    greek_life_available: bool = Field(
        default=False, description="Greek life available"
    )

    # Athletics
    athletic_division: Optional[str] = Field(
        None, max_length=20, description="Athletic division (D1, D2, D3)"
    )
    athletic_conferences: Optional[List[str]] = Field(
        None, description="Athletic conferences"
    )

    # Rankings and Recognition
    us_news_ranking: Optional[int] = Field(None, ge=1, description="US News ranking")
    forbes_ranking: Optional[int] = Field(None, ge=1, description="Forbes ranking")
    other_rankings: Optional[Dict[str, Any]] = Field(None, description="Other rankings")

    # Outcomes
    graduation_rate_4_year: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="4-year graduation rate"
    )
    graduation_rate_6_year: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="6-year graduation rate"
    )
    retention_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Student retention rate"
    )
    employment_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Graduate employment rate"
    )
    avg_starting_salary: Optional[int] = Field(
        None, ge=0, description="Average starting salary"
    )

    # Diversity
    percent_white: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percent white students"
    )
    percent_black: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percent Black students"
    )
    percent_hispanic: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percent Hispanic students"
    )
    percent_asian: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percent Asian students"
    )
    percent_international: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percent international students"
    )

    # Application Information
    application_deadline: Optional[str] = Field(
        None, max_length=50, description="Application deadline"
    )
    early_decision_deadline: Optional[str] = Field(
        None, max_length=50, description="Early decision deadline"
    )
    early_action_deadline: Optional[str] = Field(
        None, max_length=50, description="Early action deadline"
    )
    application_fee: Optional[int] = Field(None, ge=0, description="Application fee")
    common_app_accepted: bool = Field(
        default=False, description="Accepts Common Application"
    )

    # Requirements
    essays_required: bool = Field(
        default=False, description="Essays required for admission"
    )
    letters_of_recommendation: Optional[int] = Field(
        None, ge=0, le=10, description="Number of recommendation letters required"
    )
    interview_required: bool = Field(
        default=False, description="Interview required for admission"
    )

    # Status
    is_active: bool = Field(default=True, description="College is active in system")
    is_verified: bool = Field(default=False, description="Data has been verified")
    data_source: Optional[str] = Field(
        None, max_length=100, description="Source of data"
    )

    # Pydantic v2 validators
    @model_validator(mode="after")
    def validate_sat_score_ranges(self) -> "CollegeCreate":
        """Validate SAT score ranges are logical"""
        if self.sat_total_25 and self.sat_total_75:
            if self.sat_total_25 > self.sat_total_75:
                raise ValueError(
                    "SAT 25th percentile cannot be higher than 75th percentile"
                )

        if self.sat_math_25 and self.sat_math_75:
            if self.sat_math_25 > self.sat_math_75:
                raise ValueError(
                    "SAT Math 25th percentile cannot be higher than 75th percentile"
                )

        if self.sat_reading_25 and self.sat_reading_75:
            if self.sat_reading_25 > self.sat_reading_75:
                raise ValueError(
                    "SAT Reading 25th percentile cannot be higher than 75th percentile"
                )

        return self

    @model_validator(mode="after")
    def validate_act_score_ranges(self) -> "CollegeCreate":
        """Validate ACT score ranges are logical"""
        if self.act_composite_25 and self.act_composite_75:
            if self.act_composite_25 > self.act_composite_75:
                raise ValueError(
                    "ACT 25th percentile cannot be higher than 75th percentile"
                )
        return self

    @model_validator(mode="after")
    def validate_enrollment_numbers(self) -> "CollegeCreate":
        """Validate enrollment numbers are logical"""
        if (
            self.undergraduate_enrollment
            and self.graduate_enrollment
            and self.total_enrollment
        ):
            calculated_total = self.undergraduate_enrollment + self.graduate_enrollment
            if abs(calculated_total - self.total_enrollment) > (
                self.total_enrollment * 0.1
            ):  # 10% tolerance
                raise ValueError(
                    "Total enrollment should approximately equal undergraduate + graduate enrollment"
                )
        return self

    @field_validator("website")
    @classmethod
    def validate_website_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation"""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            return f"https://{v}"
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
    """Schema for updating college information - all fields optional"""

    # Basic Information
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

    # Most commonly updated fields
    total_enrollment: Optional[int] = Field(None, ge=0)
    acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    tuition_in_state: Optional[int] = Field(None, ge=0)
    tuition_out_of_state: Optional[int] = Field(None, ge=0)
    available_majors: Optional[List[str]] = None
    us_news_ranking: Optional[int] = Field(None, ge=1)

    # Status fields
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @field_validator("website")
    @classmethod
    def validate_website_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation"""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            return f"https://{v}"
        return v


class CollegeResponse(CollegeBase):
    """Complete schema for college API responses"""

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
    sat_math_25: Optional[int] = None
    sat_math_75: Optional[int] = None
    sat_reading_25: Optional[int] = None
    sat_reading_75: Optional[int] = None
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

    # Computed properties (from model)
    display_name: Optional[str] = None
    location_display: Optional[str] = None
    sat_range_display: Optional[str] = None
    act_range_display: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# SEARCH AND FILTER SCHEMAS
# ==========================================


class CollegeSearchFilter(BaseModel):
    """Comprehensive college search and filtering schema"""

    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    # Basic filters
    active_only: bool = Field(default=True, description="Only active colleges")
    verified_only: bool = Field(default=False, description="Only verified colleges")

    # Search
    search_query: Optional[str] = Field(
        None, min_length=2, max_length=255, description="Search term"
    )

    # Location filters
    state: Optional[str] = Field(None, description="Filter by state")
    region: Optional[str] = Field(None, description="Filter by region")
    campus_setting: Optional[str] = Field(None, description="Urban/Suburban/Rural")

    # Institution type filters
    college_type: Optional[CollegeTypeEnum] = Field(
        None, description="Institution type"
    )
    college_size: Optional[CollegeSizeEnum] = Field(
        None, description="College size category"
    )

    # Academic filters
    min_acceptance_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum acceptance rate"
    )
    max_acceptance_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Maximum acceptance rate"
    )
    admission_difficulty: Optional[AdmissionDifficultyEnum] = Field(
        None, description="Admission difficulty"
    )

    # Student profile matching
    student_gpa: Optional[float] = Field(
        None, ge=0.0, le=5.0, description="Student GPA for matching"
    )
    student_sat_score: Optional[int] = Field(
        None, ge=400, le=1600, description="Student SAT score"
    )
    student_act_score: Optional[int] = Field(
        None, ge=1, le=36, description="Student ACT score"
    )
    student_major: Optional[str] = Field(None, description="Student's intended major")
    student_state: Optional[str] = Field(None, description="Student's home state")

    # Financial filters
    max_tuition_in_state: Optional[int] = Field(
        None, ge=0, description="Max in-state tuition"
    )
    max_tuition_out_of_state: Optional[int] = Field(
        None, ge=0, description="Max out-of-state tuition"
    )
    max_total_cost: Optional[int] = Field(None, ge=0, description="Max total cost")

    # Program filters
    required_majors: Optional[List[str]] = Field(
        None, description="Required available majors"
    )
    strong_programs_only: Optional[bool] = Field(
        None, description="Only colleges with strong programs"
    )

    # Size filters
    min_enrollment: Optional[int] = Field(None, ge=0, description="Minimum enrollment")
    max_enrollment: Optional[int] = Field(None, ge=0, description="Maximum enrollment")

    # Diversity filters
    historically_black: Optional[bool] = Field(None, description="HBCU filter")
    hispanic_serving: Optional[bool] = Field(None, description="HSI filter")
    tribal_college: Optional[bool] = Field(None, description="Tribal college filter")
    women_only: Optional[bool] = Field(None, description="Women-only filter")
    men_only: Optional[bool] = Field(None, description="Men-only filter")

    # Athletics
    athletic_division: Optional[str] = Field(None, description="Athletic division")

    # Outcomes
    min_graduation_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum graduation rate"
    )
    min_retention_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum retention rate"
    )

    # Sorting
    sort_by: str = Field(default="name", description="Field to sort by")
    sort_order: SortOrderEnum = Field(
        default=SortOrderEnum.ASC, description="Sort direction"
    )

    @model_validator(mode="after")
    def validate_acceptance_rate_range(self) -> "CollegeSearchFilter":
        """Validate acceptance rate range"""
        if (
            self.min_acceptance_rate is not None
            and self.max_acceptance_rate is not None
            and self.min_acceptance_rate > self.max_acceptance_rate
        ):
            raise ValueError(
                "min_acceptance_rate cannot be greater than max_acceptance_rate"
            )
        return self

    @model_validator(mode="after")
    def validate_enrollment_range(self) -> "CollegeSearchFilter":
        """Validate enrollment range"""
        if (
            self.min_enrollment is not None
            and self.max_enrollment is not None
            and self.min_enrollment > self.max_enrollment
        ):
            raise ValueError("min_enrollment cannot be greater than max_enrollment")
        return self


# ==========================================
# COLLEGE MATCH SCHEMAS
# ==========================================


class CollegeMatchCreate(BaseModel):
    """Schema for creating college matches"""

    user_id: int = Field(..., gt=0, description="User ID")
    college_id: int = Field(..., gt=0, description="College ID")
    match_score: float = Field(..., ge=0.0, le=100.0, description="Match score (0-100)")
    match_category: Optional[MatchCategoryEnum] = Field(
        None, description="Match category"
    )
    match_reasons: Optional[List[str]] = Field(
        None, description="Reasons for the match"
    )
    concerns: Optional[List[str]] = Field(None, description="Potential concerns")


class CollegeMatchUpdate(BaseModel):
    """Schema for updating college match interactions"""

    viewed: Optional[bool] = Field(None, description="Mark as viewed")
    interested: Optional[bool] = Field(None, description="Interest level")
    applied: Optional[bool] = Field(None, description="Applied status")
    bookmarked: Optional[bool] = Field(None, description="Bookmarked status")
    application_status: Optional[str] = Field(
        None, max_length=50, description="Application status"
    )
    application_deadline: Optional[datetime] = Field(
        None, description="Application deadline"
    )
    user_notes: Optional[str] = Field(None, max_length=2000, description="User notes")


class CollegeMatchResponse(BaseModel):
    """Schema for college match API responses"""

    id: int
    user_id: int
    college_id: int
    college: CollegeResponse

    # Match scoring
    match_score: float
    match_category: Optional[MatchCategoryEnum] = None
    match_reasons: Optional[List[str]] = None
    concerns: Optional[List[str]] = None

    # User interactions
    viewed: bool
    interested: Optional[bool] = None
    applied: bool
    bookmarked: bool

    # Application tracking
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
    """Summary statistics for user's college matches"""

    user_id: int
    total_matches: int
    safety_schools: int
    match_schools: int
    reach_schools: int

    # Engagement metrics
    viewed_count: int
    applied_count: int
    bookmarked_count: int
    interested_count: int

    # Score metrics
    average_match_score: float
    best_match_score: float

    # Recent activity
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

    colleges: List[CollegeCreate] = Field(
        ..., min_length=1, max_length=100, description="List of colleges to create"
    )


class CollegeBatchResponse(BaseModel):
    """Response schema for batch operations"""

    success_count: int = Field(..., ge=0, description="Number of successful operations")
    error_count: int = Field(..., ge=0, description="Number of failed operations")
    errors: Optional[List[str]] = Field(None, description="List of error messages")
    created_ids: Optional[List[int]] = Field(
        None, description="List of created college IDs"
    )


class CollegeStatistics(BaseModel):
    """College platform statistics schema"""

    total_colleges: int = Field(..., ge=0)
    active_colleges: int = Field(..., ge=0)
    verified_colleges: int = Field(..., ge=0)
    colleges_by_type: Dict[str, int] = Field(..., description="Count by college type")
    colleges_by_size: Dict[str, int] = Field(..., description="Count by college size")
    colleges_by_state: Dict[str, int] = Field(
        ..., description="Count by state (top 10)"
    )
    avg_acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    avg_tuition_public: Optional[int] = Field(None, ge=0)
    avg_tuition_private: Optional[int] = Field(None, ge=0)


# ==========================================
# RECOMMENDATION SCHEMAS
# ==========================================


class CollegeRecommendationRequest(BaseModel):
    """Request schema for college recommendations"""

    user_id: Optional[int] = Field(
        None, gt=0, description="User ID (use current user if None)"
    )
    limit: int = Field(default=20, ge=1, le=100, description="Maximum recommendations")
    include_safety: bool = Field(default=True, description="Include safety schools")
    include_match: bool = Field(default=True, description="Include match schools")
    include_reach: bool = Field(default=True, description="Include reach schools")
    force_recalculate: bool = Field(
        default=False, description="Force recalculation of matches"
    )


class CollegeRecommendationResponse(BaseModel):
    """Response schema for college recommendations"""

    recommendations: List[CollegeMatchResponse] = Field(
        ..., description="List of recommended colleges"
    )
    summary: CollegeMatchSummary = Field(..., description="Summary of user's matches")
    total_colleges_analyzed: int = Field(
        ..., ge=0, description="Total colleges analyzed"
    )
    recommendation_generated_at: datetime = Field(
        ..., description="When recommendations were generated"
    )
