# app/schemas/college.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ===========================
# ENUMS
# ===========================


class CollegeType(str, Enum):
    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"


class CollegeSize(str, Enum):
    VERY_SMALL = "very_small"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


class CarnegieClassification(str, Enum):
    R1_VERY_HIGH_RESEARCH = "r1_very_high_research"
    R2_HIGH_RESEARCH = "r2_high_research"
    DOCTORAL_PROFESSIONAL = "doctoral_professional"
    MASTERS_LARGE = "masters_large"
    MASTERS_MEDIUM = "masters_medium"
    MASTERS_SMALL = "masters_small"
    BACCALAUREATE_ARTS_SCIENCES = "baccalaureate_arts_sciences"
    BACCALAUREATE_DIVERSE = "baccalaureate_diverse"
    ASSOCIATES_HIGH_TRANSFER = "associates_high_transfer"
    ASSOCIATES_MIXED = "associates_mixed"
    ASSOCIATES_HIGH_CAREER = "associates_high_career"
    SPECIAL_FOCUS = "special_focus"


class CampusSetting(str, Enum):
    URBAN = "Urban"
    SUBURBAN = "Suburban"
    RURAL = "Rural"


# ===========================
# BASE SCHEMAS
# ===========================


class CollegeBase(BaseModel):
    """Base schema for college data"""

    name: str = Field(..., min_length=1, max_length=255)
    alias: Optional[str] = None
    website: Optional[str] = None

    # Location
    address: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip_code: Optional[str] = None
    region: Optional[str] = None

    # Institution characteristics
    college_type: CollegeType
    size_category: Optional[CollegeSize] = None
    carnegie_classification: Optional[CarnegieClassification] = None

    # Special designations
    is_hbcu: bool = False
    is_hsi: bool = False
    is_tribal: bool = False
    is_women_only: bool = False
    is_men_only: bool = False
    is_religious: bool = False
    religious_affiliation: Optional[str] = None

    # Enrollment
    total_enrollment: Optional[int] = Field(None, ge=0)
    undergraduate_enrollment: Optional[int] = Field(None, ge=0)
    graduate_enrollment: Optional[int] = Field(None, ge=0)
    percent_women: Optional[float] = Field(None, ge=0, le=100)
    percent_men: Optional[float] = Field(None, ge=0, le=100)

    # Admissions
    acceptance_rate: Optional[float] = Field(None, ge=0, le=100)
    yield_rate: Optional[float] = Field(None, ge=0, le=100)

    # Test scores
    sat_reading_25: Optional[int] = Field(None, ge=200, le=800)
    sat_reading_75: Optional[int] = Field(None, ge=200, le=800)
    sat_math_25: Optional[int] = Field(None, ge=200, le=800)
    sat_math_75: Optional[int] = Field(None, ge=200, le=800)
    sat_total_25: Optional[int] = Field(None, ge=400, le=1600)
    sat_total_75: Optional[int] = Field(None, ge=400, le=1600)

    act_composite_25: Optional[int] = Field(None, ge=1, le=36)
    act_composite_75: Optional[int] = Field(None, ge=1, le=36)
    act_english_25: Optional[int] = Field(None, ge=1, le=36)
    act_english_75: Optional[int] = Field(None, ge=1, le=36)
    act_math_25: Optional[int] = Field(None, ge=1, le=36)
    act_math_75: Optional[int] = Field(None, ge=1, le=36)

    # Requirements
    requires_sat_act: bool = True
    is_test_optional: bool = False
    requires_essay: bool = False
    requires_interview: bool = False

    # Financial
    tuition_in_state: Optional[int] = Field(None, ge=0)
    tuition_out_state: Optional[int] = Field(None, ge=0)
    required_fees: Optional[int] = Field(None, ge=0)
    room_and_board: Optional[int] = Field(None, ge=0)
    total_cost_in_state: Optional[int] = Field(None, ge=0)
    total_cost_out_state: Optional[int] = Field(None, ge=0)

    # Financial aid
    percent_receiving_aid: Optional[float] = Field(None, ge=0, le=100)
    average_aid_amount: Optional[int] = Field(None, ge=0)
    percent_need_met: Optional[float] = Field(None, ge=0, le=100)

    # Academics
    student_faculty_ratio: Optional[float] = Field(None, ge=1)
    graduation_rate_4_year: Optional[float] = Field(None, ge=0, le=100)
    graduation_rate_6_year: Optional[float] = Field(None, ge=0, le=100)
    retention_rate: Optional[float] = Field(None, ge=0, le=100)

    # Academic programs
    popular_majors: Optional[List[str]] = None
    all_majors_offered: Optional[List[str]] = None
    offers_online_degrees: bool = False
    offers_part_time: bool = False
    offers_weekend_college: bool = False

    # Campus life
    campus_setting: Optional[CampusSetting] = None
    campus_size_acres: Optional[int] = Field(None, ge=0)
    percent_students_on_campus: Optional[float] = Field(None, ge=0, le=100)
    housing_required: bool = False

    # Athletics
    ncaa_division: Optional[str] = None
    athletic_conference: Optional[str] = None

    # Outcomes
    median_earnings_6_years: Optional[int] = Field(None, ge=0)
    median_earnings_10_years: Optional[int] = Field(None, ge=0)
    employment_rate: Optional[float] = Field(None, ge=0, le=100)

    # Rankings and scores
    rankings_data: Optional[Dict[str, Any]] = None
    competitiveness_score: Optional[float] = Field(None, ge=0, le=100)
    affordability_score: Optional[float] = Field(None, ge=0, le=100)
    value_score: Optional[float] = Field(None, ge=0, le=100)

    # Metadata
    data_year: Optional[int] = 2023
    is_active: bool = True
    is_verified: bool = False
    data_completeness: Optional[float] = Field(None, ge=0, le=1)


class CollegeCreate(CollegeBase):
    """Schema for creating colleges (data import)"""

    unitid: int = Field(..., description="IPEDS UNITID")

    class Config:
        json_schema_extra = {
            "example": {
                "unitid": 100654,
                "name": "Harvard University",
                "city": "Cambridge",
                "state": "MA",
                "college_type": "private_nonprofit",
                "total_enrollment": 23000,
                "acceptance_rate": 5.0,
                "sat_total_75": 1580,
                "tuition_out_state": 57261,
                "graduation_rate_6_year": 97.0,
            }
        }


class CollegeUpdate(BaseModel):
    """Schema for updating college information"""

    name: Optional[str] = None
    website: Optional[str] = None
    total_enrollment: Optional[int] = None
    acceptance_rate: Optional[float] = None
    tuition_in_state: Optional[int] = None
    tuition_out_state: Optional[int] = None
    is_verified: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "website": "https://www.harvard.edu",
                "total_enrollment": 23500,
                "is_verified": True,
            }
        }


class CollegeResponse(CollegeBase):
    """Schema for college API responses"""

    id: int
    unitid: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    # Computed properties
    location_string: Optional[str] = None
    sat_range_string: Optional[str] = None
    act_range_string: Optional[str] = None
    size_description: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "unitid": 100654,
                "name": "Harvard University",
                "city": "Cambridge",
                "state": "MA",
                "college_type": "private_nonprofit",
                "total_enrollment": 23000,
                "acceptance_rate": 5.0,
                "sat_total_75": 1580,
                "tuition_out_state": 57261,
                "graduation_rate_6_year": 97.0,
                "location_string": "Cambridge, MA",
                "sat_range_string": "1460-1580",
                "size_description": "Large (23,000 students)",
                "created_at": "2025-01-15T10:00:00Z",
            }
        }


# ===========================
# SEARCH SCHEMAS
# ===========================


class CollegeSearchFilters(BaseModel):
    """Comprehensive college search filters"""

    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Results per page")

    # Text search
    search_query: Optional[str] = Field(
        None, description="Search college names, cities, etc."
    )

    # Location filters
    state: Optional[List[str]] = Field(
        None, description="State abbreviations (e.g., ['CA', 'NY'])"
    )
    city: Optional[str] = Field(None, description="City name (partial match)")
    region: Optional[str] = Field(None, description="Geographic region")

    # Institution type
    college_type: Optional[List[CollegeType]] = Field(
        None, description="Public, private, etc."
    )
    size_category: Optional[List[CollegeSize]] = Field(
        None, description="Enrollment size categories"
    )
    carnegie_classification: Optional[CarnegieClassification] = None

    # Special designations
    hbcu_only: bool = Field(False, description="Show only HBCUs")
    hsi_only: bool = Field(False, description="Show only Hispanic Serving Institutions")
    women_only: bool = Field(False, description="Show only women's colleges")
    religious_only: bool = Field(False, description="Show only religious institutions")

    # Enrollment
    min_enrollment: Optional[int] = Field(
        None, ge=0, description="Minimum total enrollment"
    )
    max_enrollment: Optional[int] = Field(
        None, ge=0, description="Maximum total enrollment"
    )

    # Academic filters
    min_acceptance_rate: Optional[float] = Field(None, ge=0, le=100)
    max_acceptance_rate: Optional[float] = Field(None, ge=0, le=100)

    # Student academic profile (for matching)
    student_gpa: Optional[float] = Field(None, ge=0, le=5, description="Student's GPA")
    student_sat_score: Optional[int] = Field(
        None, ge=400, le=1600, description="Student's SAT score"
    )
    student_act_score: Optional[int] = Field(
        None, ge=1, le=36, description="Student's ACT score"
    )

    # Financial filters
    max_tuition: Optional[int] = Field(None, ge=0, description="Maximum tuition")
    max_total_cost: Optional[int] = Field(None, ge=0, description="Maximum total cost")
    in_state_student: bool = Field(False, description="Student is in-state resident")

    # Academic programs
    major_interest: Optional[str] = Field(None, description="Intended major")

    # Campus features
    urban_setting: bool = Field(False, description="Urban campus setting only")
    requires_on_campus_housing: Optional[bool] = None
    ncaa_division: Optional[str] = Field(None, description="NCAA division (I, II, III)")

    # Application requirements
    test_optional_only: bool = Field(False, description="Test-optional schools only")

    # Sorting
    sort_by: str = Field(
        "name",
        pattern="^(name|acceptance_rate|tuition|enrollment|sat_score|graduation_rate|competitiveness|affordability|value|created_at)$",
    )
    sort_order: str = Field("asc", pattern="^(asc|desc)$")

    @field_validator("state")
    @classmethod
    def validate_states(cls, v):
        if v:
            # Convert to uppercase and validate format
            return [state.upper() for state in v if len(state) == 2]
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "search_query": "engineering",
                "state": ["CA", "MA"],
                "college_type": ["public", "private_nonprofit"],
                "min_enrollment": 5000,
                "max_acceptance_rate": 50.0,
                "student_gpa": 3.7,
                "student_sat_score": 1350,
                "max_total_cost": 40000,
                "major_interest": "Computer Science",
                "sort_by": "acceptance_rate",
                "sort_order": "asc",
                "page": 1,
                "limit": 20,
            }
        }


class CollegeSearchResponse(BaseModel):
    """Schema for college search results"""

    colleges: List[CollegeResponse]
    pagination: Dict[str, Any]
    search_metadata: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "colleges": [
                    {
                        "id": 1,
                        "name": "MIT",
                        "city": "Cambridge",
                        "state": "MA",
                        "acceptance_rate": 7.3,
                        "sat_range_string": "1510-1580",
                    }
                ],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 5,
                    "total_results": 98,
                    "has_next": True,
                    "has_previous": False,
                },
                "search_metadata": {
                    "statistics": {
                        "acceptance_rate": {"min": 5.0, "max": 50.0, "avg": 27.5}
                    },
                    "distributions": {
                        "by_type": {"public": 45, "private_nonprofit": 53}
                    },
                },
            }
        }


# ===========================
# FAVORITES & SAVED SEARCHES
# ===========================


class CollegeFavoriteCreate(BaseModel):
    """Schema for adding college to favorites"""

    college_id: int
    notes: Optional[str] = Field(None, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "college_id": 1,
                "notes": "Great engineering program, visited campus in fall 2024",
            }
        }


class CollegeFavoriteResponse(BaseModel):
    """Schema for favorite college response"""

    id: int
    user_id: int
    college_id: int
    notes: Optional[str] = None
    created_at: datetime
    college: CollegeResponse

    class Config:
        from_attributes = True


class CollegeSavedSearchCreate(BaseModel):
    """Schema for saving a college search"""

    search_name: str = Field(..., min_length=1, max_length=100)
    search_criteria: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "search_name": "Engineering Schools in California",
                "search_criteria": {
                    "state": ["CA"],
                    "major_interest": "Engineering",
                    "max_total_cost": 50000,
                },
            }
        }


class CollegeSavedSearchResponse(BaseModel):
    """Schema for saved search response"""

    id: int
    user_id: int
    search_name: str
    search_criteria: Dict[str, Any]
    results_count: Optional[int] = None
    created_at: datetime
    last_run_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===========================
# COMPARISON & MATCHING
# ===========================


class CollegeComparisonRequest(BaseModel):
    """Schema for comparing colleges"""

    college_ids: List[int] = Field(..., min_length=2, max_length=10)
    comparison_categories: Optional[List[str]] = Field(
        default=["academics", "admissions", "financial", "campus_life"],
        description="Categories to compare",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "college_ids": [1, 2, 3],
                "comparison_categories": ["academics", "admissions", "financial"],
            }
        }


class CollegeMatchRequest(BaseModel):
    """Schema for finding college matches based on student profile"""

    # Student academic profile
    gpa: Optional[float] = Field(None, ge=0, le=5)
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    intended_major: Optional[str] = None

    # Preferences
    preferred_states: Optional[List[str]] = None
    preferred_regions: Optional[List[str]] = None
    preferred_size: Optional[CollegeSize] = None
    preferred_setting: Optional[CampusSetting] = None
    max_budget: Optional[int] = Field(None, ge=0)

    # Special preferences
    prefer_hbcu: bool = False
    prefer_women_college: bool = False
    prefer_religious: bool = False

    # Search parameters
    match_threshold: float = Field(
        50.0, ge=0, le=100, description="Minimum match score"
    )
    max_results: int = Field(50, ge=1, le=200)

    class Config:
        json_schema_extra = {
            "example": {
                "gpa": 3.7,
                "sat_score": 1350,
                "intended_major": "Computer Science",
                "preferred_states": ["CA", "MA", "NY"],
                "preferred_size": "medium",
                "max_budget": 45000,
                "match_threshold": 60.0,
                "max_results": 25,
            }
        }


class CollegeMatchResponse(BaseModel):
    """Schema for college match results"""

    college: CollegeResponse
    match_score: float = Field(..., ge=0, le=100)
    match_reasons: List[str]
    category_scores: Dict[str, float]

    class Config:
        json_schema_extra = {
            "example": {
                "college": {"id": 1, "name": "UC Berkeley", "state": "CA"},
                "match_score": 87.5,
                "match_reasons": [
                    "Strong Computer Science program",
                    "Within budget range",
                    "Good academic fit for your GPA/test scores",
                ],
                "category_scores": {
                    "academic": 90.0,
                    "financial": 85.0,
                    "location": 88.0,
                    "culture": 87.0,
                },
            }
        }


# ===========================
# ANALYTICS SCHEMAS
# ===========================


class CollegeInsightsResponse(BaseModel):
    """Schema for search insights and suggestions"""

    total_results: int
    suggestions: List[str]
    alternative_searches: Optional[List[Dict[str, Any]]] = None
    market_analysis: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_results": 3,
                "suggestions": [
                    "Consider expanding your search criteria to find more options",
                    "Try including less selective schools (higher acceptance rates)",
                ],
                "alternative_searches": [
                    {
                        "name": "Expand to neighboring states",
                        "criteria": {"state": ["CA", "NV", "OR"]},
                    },
                    {
                        "name": "Include more school types",
                        "criteria": {"college_type": ["public", "private_nonprofit"]},
                    },
                ],
            }
        }


class BulkCollegeCreate(BaseModel):
    """Schema for bulk college creation (data import)"""

    colleges: List[CollegeCreate]

    @field_validator("colleges")
    @classmethod
    def validate_colleges_list(cls, v):
        if len(v) == 0:
            raise ValueError("At least one college is required")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 colleges per batch")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "colleges": [
                    {
                        "unitid": 100654,
                        "name": "Harvard University",
                        "city": "Cambridge",
                        "state": "MA",
                        "college_type": "private_nonprofit",
                    }
                ]
            }
        }
