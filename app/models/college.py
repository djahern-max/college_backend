# app/models/college.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class CollegeType(str, Enum):
    """Types of colleges/universities"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"


class CollegeSize(str, Enum):
    """College enrollment size categories"""

    VERY_SMALL = "very_small"  # <1,000
    SMALL = "small"  # 1,000-2,999
    MEDIUM = "medium"  # 3,000-9,999
    LARGE = "large"  # 10,000-19,999
    VERY_LARGE = "very_large"  # 20,000+


class CarnegieClassification(str, Enum):
    """Simplified Carnegie Classifications"""

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


class College(Base):
    """
    College/University model with comprehensive search and matching data
    """

    __tablename__ = "colleges"

    # ===========================
    # PRIMARY KEY & IDENTIFIERS
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    unitid = Column(Integer, unique=True, nullable=False, index=True)  # IPEDS UNITID

    # ===========================
    # BASIC INFORMATION
    # ===========================
    name = Column(String(255), nullable=False, index=True)
    alias = Column(String(255), nullable=True)  # Alternative names
    website = Column(String(500), nullable=True)

    # ===========================
    # LOCATION
    # ===========================
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    zip_code = Column(String(10), nullable=True)
    region = Column(String(50), nullable=True)  # Northeast, South, etc.

    # ===========================
    # INSTITUTION CHARACTERISTICS
    # ===========================
    college_type = Column(SQLEnum(CollegeType), nullable=False, index=True)
    size_category = Column(SQLEnum(CollegeSize), nullable=True, index=True)
    carnegie_classification = Column(
        SQLEnum(CarnegieClassification), nullable=True, index=True
    )

    # Special designations
    is_hbcu = Column(Boolean, default=False)  # Historically Black College/University
    is_hsi = Column(Boolean, default=False)  # Hispanic Serving Institution
    is_tribal = Column(Boolean, default=False)  # Tribal College
    is_women_only = Column(Boolean, default=False)
    is_men_only = Column(Boolean, default=False)
    is_religious = Column(Boolean, default=False)
    religious_affiliation = Column(String(100), nullable=True)

    # ===========================
    # ENROLLMENT DATA
    # ===========================
    total_enrollment = Column(Integer, nullable=True)
    undergraduate_enrollment = Column(Integer, nullable=True)
    graduate_enrollment = Column(Integer, nullable=True)
    percent_women = Column(Float, nullable=True)
    percent_men = Column(Float, nullable=True)

    # ===========================
    # ADMISSIONS DATA
    # ===========================
    acceptance_rate = Column(Float, nullable=True)  # 0-100
    yield_rate = Column(Float, nullable=True)  # 0-100

    # Test scores (25th-75th percentile)
    sat_reading_25 = Column(Integer, nullable=True)
    sat_reading_75 = Column(Integer, nullable=True)
    sat_math_25 = Column(Integer, nullable=True)
    sat_math_75 = Column(Integer, nullable=True)
    sat_total_25 = Column(Integer, nullable=True)  # Combined
    sat_total_75 = Column(Integer, nullable=True)  # Combined

    act_composite_25 = Column(Integer, nullable=True)
    act_composite_75 = Column(Integer, nullable=True)
    act_english_25 = Column(Integer, nullable=True)
    act_english_75 = Column(Integer, nullable=True)
    act_math_25 = Column(Integer, nullable=True)
    act_math_75 = Column(Integer, nullable=True)

    # Admissions requirements
    requires_sat_act = Column(Boolean, default=True)
    is_test_optional = Column(Boolean, default=False)
    requires_essay = Column(Boolean, default=False)
    requires_interview = Column(Boolean, default=False)

    # ===========================
    # FINANCIAL INFORMATION
    # ===========================
    tuition_in_state = Column(Integer, nullable=True)
    tuition_out_state = Column(Integer, nullable=True)
    required_fees = Column(Integer, nullable=True)
    room_and_board = Column(Integer, nullable=True)
    total_cost_in_state = Column(Integer, nullable=True)
    total_cost_out_state = Column(Integer, nullable=True)

    # Financial aid
    percent_receiving_aid = Column(Float, nullable=True)
    average_aid_amount = Column(Integer, nullable=True)
    percent_need_met = Column(Float, nullable=True)

    # ===========================
    # ACADEMICS
    # ===========================
    student_faculty_ratio = Column(Float, nullable=True)
    graduation_rate_4_year = Column(Float, nullable=True)
    graduation_rate_6_year = Column(Float, nullable=True)
    retention_rate = Column(Float, nullable=True)

    # Popular majors (JSON array)
    popular_majors = Column(ARRAY(String), nullable=True)
    all_majors_offered = Column(ARRAY(String), nullable=True)

    # Academic programs
    offers_online_degrees = Column(Boolean, default=False)
    offers_part_time = Column(Boolean, default=False)
    offers_weekend_college = Column(Boolean, default=False)

    # ===========================
    # CAMPUS LIFE
    # ===========================
    campus_setting = Column(String(50), nullable=True)  # Urban, Suburban, Rural
    campus_size_acres = Column(Integer, nullable=True)

    # Housing
    percent_students_on_campus = Column(Float, nullable=True)
    housing_required = Column(Boolean, default=False)

    # Athletics
    ncaa_division = Column(String(10), nullable=True)  # I, II, III
    athletic_conference = Column(String(100), nullable=True)

    # ===========================
    # OUTCOMES & RANKINGS
    # ===========================
    median_earnings_6_years = Column(Integer, nullable=True)
    median_earnings_10_years = Column(Integer, nullable=True)
    employment_rate = Column(Float, nullable=True)

    # Rankings (store as JSON for flexibility)
    rankings_data = Column(JSON, nullable=True)

    # ===========================
    # SEARCH & MATCHING
    # ===========================
    # Pre-calculated search fields
    competitiveness_score = Column(Float, nullable=True)  # 0-100
    affordability_score = Column(Float, nullable=True)  # 0-100
    value_score = Column(Float, nullable=True)  # 0-100

    # Search keywords for full-text search
    search_keywords = Column(ARRAY(String), nullable=True)

    # ===========================
    # METADATA
    # ===========================
    data_year = Column(Integer, default=2023)  # IPEDS data year
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Data completeness score
    data_completeness = Column(Float, nullable=True)  # 0-1

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<College(id={self.id}, name='{self.name}', state='{self.state}')>"

    # ===========================
    # COMPUTED PROPERTIES
    # ===========================

    @property
    def location_string(self) -> str:
        """Return formatted location string"""
        return f"{self.city}, {self.state}"

    @property
    def sat_range_string(self) -> Optional[str]:
        """Return SAT range as string"""
        if self.sat_total_25 and self.sat_total_75:
            return f"{self.sat_total_25}-{self.sat_total_75}"
        return None

    @property
    def act_range_string(self) -> Optional[str]:
        """Return ACT range as string"""
        if self.act_composite_25 and self.act_composite_75:
            return f"{self.act_composite_25}-{self.act_composite_75}"
        return None

    @property
    def is_affordable(self) -> bool:
        """Quick affordability check"""
        if self.total_cost_in_state:
            return self.total_cost_in_state <= 30000
        return False

    @property
    def is_highly_selective(self) -> bool:
        """Check if highly selective (acceptance rate <= 25%)"""
        return self.acceptance_rate is not None and self.acceptance_rate <= 25

    @property
    def size_description(self) -> str:
        """Return human-readable size description"""
        if not self.total_enrollment:
            return "Size not available"

        if self.total_enrollment < 1000:
            return f"Very Small ({self.total_enrollment:,} students)"
        elif self.total_enrollment < 3000:
            return f"Small ({self.total_enrollment:,} students)"
        elif self.total_enrollment < 10000:
            return f"Medium ({self.total_enrollment:,} students)"
        elif self.total_enrollment < 20000:
            return f"Large ({self.total_enrollment:,} students)"
        else:
            return f"Very Large ({self.total_enrollment:,} students)"


class CollegeSavedSearch(Base):
    """User's saved college searches"""

    __tablename__ = "college_saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # FK to users table
    search_name = Column(String(100), nullable=False)
    search_criteria = Column(JSON, nullable=False)  # Store search parameters
    results_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_run_at = Column(DateTime(timezone=True), nullable=True)


class CollegeFavorite(Base):
    """User's favorite/bookmarked colleges"""

    __tablename__ = "college_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # FK to users table
    college_id = Column(Integer, nullable=False, index=True)  # FK to colleges table
    notes = Column(Text, nullable=True)  # User's personal notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships would be added when integrating with user system
    # college = relationship("College")
    # user = relationship("User")
