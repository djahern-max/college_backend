# app/models/college.py - CLEAN CONVENTIONAL VERSION
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CollegeType(str, Enum):
    """Types of colleges and universities"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"
    COMMUNITY_COLLEGE = "community_college"


class CollegeSize(str, Enum):
    """College size categories"""

    SMALL = "small"  # Under 2,000
    MEDIUM = "medium"  # 2,000 - 15,000
    LARGE = "large"  # Over 15,000


class AdmissionDifficulty(str, Enum):
    """Admission difficulty levels"""

    MOST_DIFFICULT = "most_difficult"  # <25% acceptance
    VERY_DIFFICULT = "very_difficult"  # 25-49% acceptance
    MODERATELY_DIFFICULT = "moderately_difficult"  # 50-74% acceptance
    MINIMALLY_DIFFICULT = "minimally_difficult"  # 75-89% acceptance
    NONCOMPETITIVE = "noncompetitive"  # >90% acceptance


class College(Base):
    """
    College/University model - Clean database-focused version
    """

    __tablename__ = "colleges"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)

    # Location
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False, index=True)
    zip_code = Column(String(10), nullable=True)
    region = Column(String(50), nullable=True, index=True)

    # Institution Type
    college_type = Column(SQLEnum(CollegeType), nullable=False, index=True)
    is_historically_black = Column(Boolean, default=False, index=True)
    is_hispanic_serving = Column(Boolean, default=False, index=True)
    is_tribal_college = Column(Boolean, default=False)
    is_women_only = Column(Boolean, default=False)
    is_men_only = Column(Boolean, default=False)

    # Size and Demographics
    total_enrollment = Column(Integer, nullable=True)
    undergraduate_enrollment = Column(Integer, nullable=True)
    graduate_enrollment = Column(Integer, nullable=True)
    college_size = Column(SQLEnum(CollegeSize), nullable=True, index=True)

    # Academic Information
    acceptance_rate = Column(Float, nullable=True, index=True)
    admission_difficulty = Column(
        SQLEnum(AdmissionDifficulty), nullable=True, index=True
    )

    # Test Score Ranges (25th-75th percentile)
    sat_math_25 = Column(Integer, nullable=True)
    sat_math_75 = Column(Integer, nullable=True)
    sat_reading_25 = Column(Integer, nullable=True)
    sat_reading_75 = Column(Integer, nullable=True)
    sat_total_25 = Column(Integer, nullable=True, index=True)
    sat_total_75 = Column(Integer, nullable=True, index=True)

    act_composite_25 = Column(Integer, nullable=True, index=True)
    act_composite_75 = Column(Integer, nullable=True, index=True)

    # GPA Requirements
    avg_gpa = Column(Float, nullable=True, index=True)
    min_gpa_recommended = Column(Float, nullable=True)

    # Financial Information
    tuition_in_state = Column(Integer, nullable=True, index=True)
    tuition_out_of_state = Column(Integer, nullable=True, index=True)
    room_and_board = Column(Integer, nullable=True)
    total_cost_in_state = Column(Integer, nullable=True, index=True)
    total_cost_out_of_state = Column(Integer, nullable=True, index=True)

    # Financial Aid
    avg_financial_aid = Column(Integer, nullable=True)
    percent_receiving_aid = Column(Float, nullable=True)
    avg_net_price = Column(Integer, nullable=True, index=True)

    # Academic Programs (using GIN indexes for array operations)
    available_majors = Column(ARRAY(String), nullable=True)
    popular_majors = Column(ARRAY(String), nullable=True)
    strong_programs = Column(ARRAY(String), nullable=True)

    # Campus Life
    campus_setting = Column(String(50), nullable=True, index=True)
    housing_guaranteed = Column(Boolean, default=False)
    greek_life_available = Column(Boolean, default=False)

    # Athletics
    athletic_division = Column(String(20), nullable=True, index=True)
    athletic_conferences = Column(ARRAY(String), nullable=True)

    # Rankings and Recognition
    us_news_ranking = Column(Integer, nullable=True, index=True)
    forbes_ranking = Column(Integer, nullable=True)
    other_rankings = Column(JSON, nullable=True)

    # Outcomes
    graduation_rate_4_year = Column(Float, nullable=True)
    graduation_rate_6_year = Column(Float, nullable=True, index=True)
    retention_rate = Column(Float, nullable=True, index=True)
    employment_rate = Column(Float, nullable=True)
    avg_starting_salary = Column(Integer, nullable=True)

    # Diversity
    percent_white = Column(Float, nullable=True)
    percent_black = Column(Float, nullable=True)
    percent_hispanic = Column(Float, nullable=True)
    percent_asian = Column(Float, nullable=True)
    percent_international = Column(Float, nullable=True)

    # Application Information
    application_deadline = Column(String(50), nullable=True)
    early_decision_deadline = Column(String(50), nullable=True)
    early_action_deadline = Column(String(50), nullable=True)
    application_fee = Column(Integer, nullable=True)
    common_app_accepted = Column(Boolean, default=False)

    # Requirements
    essays_required = Column(Boolean, default=False)
    letters_of_recommendation = Column(Integer, nullable=True)
    interview_required = Column(Boolean, default=False)

    # Status and Verification
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    data_source = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    college_matches = relationship(
        "CollegeMatch", back_populates="college", cascade="all, delete-orphan"
    )

    # Database constraints and indexes
    __table_args__ = (
        # Check constraints for data integrity
        CheckConstraint(
            "acceptance_rate >= 0 AND acceptance_rate <= 1",
            name="check_acceptance_rate_range",
        ),
        CheckConstraint("avg_gpa >= 0 AND avg_gpa <= 5", name="check_gpa_range"),
        CheckConstraint(
            "sat_total_25 >= 400 AND sat_total_25 <= 1600",
            name="check_sat_total_25_range",
        ),
        CheckConstraint(
            "sat_total_75 >= 400 AND sat_total_75 <= 1600",
            name="check_sat_total_75_range",
        ),
        CheckConstraint("sat_total_25 <= sat_total_75", name="check_sat_range_order"),
        CheckConstraint(
            "act_composite_25 >= 1 AND act_composite_25 <= 36",
            name="check_act_25_range",
        ),
        CheckConstraint(
            "act_composite_75 >= 1 AND act_composite_75 <= 36",
            name="check_act_75_range",
        ),
        CheckConstraint(
            "act_composite_25 <= act_composite_75", name="check_act_range_order"
        ),
        CheckConstraint(
            "graduation_rate_4_year >= 0 AND graduation_rate_4_year <= 1",
            name="check_grad_rate_4_range",
        ),
        CheckConstraint(
            "graduation_rate_6_year >= 0 AND graduation_rate_6_year <= 1",
            name="check_grad_rate_6_range",
        ),
        CheckConstraint(
            "retention_rate >= 0 AND retention_rate <= 1",
            name="check_retention_rate_range",
        ),
        CheckConstraint(
            "tuition_in_state >= 0", name="check_tuition_in_state_positive"
        ),
        CheckConstraint(
            "tuition_out_of_state >= 0", name="check_tuition_out_state_positive"
        ),
        CheckConstraint("total_enrollment >= 0", name="check_enrollment_positive"),
        # Composite indexes for common query patterns
        Index("idx_college_search", "is_active", "college_type", "state"),
        Index("idx_college_academic", "acceptance_rate", "avg_gpa", "sat_total_25"),
        Index(
            "idx_college_financial",
            "tuition_in_state",
            "tuition_out_of_state",
            "avg_net_price",
        ),
        Index("idx_college_outcomes", "graduation_rate_6_year", "retention_rate"),
        Index("idx_college_rankings", "us_news_ranking", "is_active"),
        # Partial indexes for active colleges only
        Index(
            "idx_active_colleges_type_state",
            "college_type",
            "state",
            postgresql_where=(Column("is_active") == True),
        ),
        Index(
            "idx_active_colleges_size_setting",
            "college_size",
            "campus_setting",
            postgresql_where=(Column("is_active") == True),
        ),
    )

    def __repr__(self):
        return f"<College(id={self.id}, name='{self.name}', state='{self.state}')>"

    # ===========================
    # SIMPLE PROPERTY METHODS (OK in models)
    # ===========================

    @property
    def display_name(self) -> str:
        """Get display name (short name if available, otherwise full name)"""
        return self.short_name or self.name

    @property
    def location_display(self) -> str:
        """Get formatted location display"""
        return f"{self.city}, {self.state}"

    @property
    def is_public(self) -> bool:
        """Check if college is public"""
        return self.college_type == CollegeType.PUBLIC

    @property
    def is_private(self) -> bool:
        """Check if college is private (non-profit or for-profit)"""
        return self.college_type in [
            CollegeType.PRIVATE_NONPROFIT,
            CollegeType.PRIVATE_FOR_PROFIT,
        ]

    @property
    def has_test_score_data(self) -> bool:
        """Check if college has test score data"""
        return bool(
            (self.sat_total_25 and self.sat_total_75)
            or (self.act_composite_25 and self.act_composite_75)
        )

    @property
    def sat_range_display(self) -> Optional[str]:
        """Get formatted SAT range display"""
        if self.sat_total_25 and self.sat_total_75:
            return f"{self.sat_total_25}-{self.sat_total_75}"
        return None

    @property
    def act_range_display(self) -> Optional[str]:
        """Get formatted ACT range display"""
        if self.act_composite_25 and self.act_composite_75:
            return f"{self.act_composite_25}-{self.act_composite_75}"
        return None

    @property
    def tuition_display(self) -> Dict[str, Optional[int]]:
        """Get tuition information formatted for display"""
        return {
            "in_state": self.tuition_in_state,
            "out_of_state": self.tuition_out_of_state,
            "has_in_state": self.tuition_in_state is not None,
            "has_out_of_state": self.tuition_out_of_state is not None,
        }

    def get_relevant_cost(self, student_state: Optional[str] = None) -> Optional[int]:
        """Get relevant cost based on student's residency - SIMPLE helper method"""
        if student_state == self.state and self.total_cost_in_state:
            return self.total_cost_in_state
        elif self.total_cost_out_of_state:
            return self.total_cost_out_of_state
        elif student_state == self.state and self.tuition_in_state:
            return self.tuition_in_state
        elif self.tuition_out_of_state:
            return self.tuition_out_of_state
        return None

    def has_major(self, major: str) -> bool:
        """Check if college offers a specific major - SIMPLE helper"""
        if not self.available_majors or not major:
            return False
        return major in self.available_majors

    def has_strong_program(self, program: str) -> bool:
        """Check if college has a strong program in area - SIMPLE helper"""
        if not self.strong_programs or not program:
            return False
        return program in self.strong_programs

    # ===========================
    # VALIDATION METHODS (OK in models)
    # ===========================

    def validate_data(self) -> List[str]:
        """Basic data validation - returns list of errors"""
        errors = []

        # Required field validation
        if not self.name or not self.name.strip():
            errors.append("College name is required")

        if not self.city or not self.city.strip():
            errors.append("City is required")

        if not self.state or not self.state.strip():
            errors.append("State is required")

        # Range validations
        if self.acceptance_rate is not None and not (0 <= self.acceptance_rate <= 1):
            errors.append("Acceptance rate must be between 0 and 1")

        if self.avg_gpa is not None and not (0 <= self.avg_gpa <= 5):
            errors.append("Average GPA must be between 0 and 5")

        # Test score validations
        if (
            self.sat_total_25
            and self.sat_total_75
            and self.sat_total_25 > self.sat_total_75
        ):
            errors.append("SAT 25th percentile cannot be higher than 75th percentile")

        if (
            self.act_composite_25
            and self.act_composite_75
            and self.act_composite_25 > self.act_composite_75
        ):
            errors.append("ACT 25th percentile cannot be higher than 75th percentile")

        return errors

    def is_valid(self) -> bool:
        """Check if college data is valid"""
        return len(self.validate_data()) == 0


class CollegeMatch(Base):
    """
    Student-College match results and tracking - Clean version
    """

    __tablename__ = "college_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False, index=True)

    # Match scoring
    match_score = Column(Float, nullable=False, index=True)
    match_category = Column(
        String(20), nullable=True, index=True
    )  # "safety", "match", "reach"
    match_reasons = Column(ARRAY(String), nullable=True)
    concerns = Column(ARRAY(String), nullable=True)

    # User interaction tracking
    viewed = Column(Boolean, default=False, index=True)
    interested = Column(Boolean, nullable=True, index=True)  # True/False/None
    applied = Column(Boolean, default=False, index=True)
    bookmarked = Column(Boolean, default=False, index=True)

    # Application status
    application_status = Column(String(50), nullable=True, index=True)
    application_deadline = Column(DateTime(timezone=True), nullable=True)

    # Notes
    user_notes = Column(Text, nullable=True)

    # Timestamps
    match_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    college = relationship("College", back_populates="college_matches")

    # Database constraints and indexes
    __table_args__ = (
        # Unique constraint to prevent duplicate matches
        Index("idx_unique_user_college_match", "user_id", "college_id", unique=True),
        # Composite indexes for common queries
        Index("idx_user_matches_by_score", "user_id", "match_score"),
        Index(
            "idx_user_matches_by_category", "user_id", "match_category", "match_score"
        ),
        Index("idx_user_interactions", "user_id", "viewed", "interested", "applied"),
        Index("idx_match_deadlines", "application_deadline", "user_id"),
        # Partial indexes for active interactions
        Index(
            "idx_viewed_matches",
            "user_id",
            "viewed_at",
            postgresql_where=(Column("viewed") == True),
        ),
        Index(
            "idx_applied_matches",
            "user_id",
            "applied_at",
            postgresql_where=(Column("applied") == True),
        ),
        Index(
            "idx_interested_matches",
            "user_id",
            "match_score",
            postgresql_where=(Column("interested") == True),
        ),
        # Check constraints
        CheckConstraint(
            "match_score >= 0 AND match_score <= 100", name="check_match_score_range"
        ),
        CheckConstraint(
            "match_category IN ('safety', 'match', 'reach')",
            name="check_match_category_values",
        ),
    )

    def __repr__(self):
        return f"<CollegeMatch(user_id={self.user_id}, college_id={self.college_id}, score={self.match_score})>"

    # ===========================
    # SIMPLE PROPERTY METHODS (OK in models)
    # ===========================

    @property
    def is_high_match(self) -> bool:
        """Check if this is a high-scoring match"""
        return self.match_score >= 80

    @property
    def is_engaged(self) -> bool:
        """Check if user has engaged with this match"""
        return self.viewed or self.interested is not None or self.bookmarked

    @property
    def days_since_match(self) -> Optional[int]:
        """Get days since match was created"""
        if not self.match_date:
            return None
        from datetime import datetime

        return (datetime.utcnow() - self.match_date.replace(tzinfo=None)).days

    @property
    def engagement_level(self) -> str:
        """Get engagement level description"""
        if self.applied:
            return "applied"
        elif self.interested is True:
            return "interested"
        elif self.viewed:
            return "viewed"
        elif self.bookmarked:
            return "bookmarked"
        else:
            return "none"

    # ===========================
    # SIMPLE HELPER METHODS (OK in models)
    # ===========================

    def mark_viewed(self):
        """Mark this match as viewed"""
        if not self.viewed:
            self.viewed = True
            self.viewed_at = func.now()

    def set_interest(self, interested: bool):
        """Set interest level"""
        self.interested = interested

    def add_bookmark(self):
        """Add to bookmarks"""
        self.bookmarked = True

    def remove_bookmark(self):
        """Remove from bookmarks"""
        self.bookmarked = False
