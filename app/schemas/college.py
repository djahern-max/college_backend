# app/schemas/college.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.college import CollegeType, CollegeSize, AdmissionDifficulty
from enum import Enum


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
