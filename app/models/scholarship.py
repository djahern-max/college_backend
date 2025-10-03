# app/models/scholarship.py - SIMPLIFIED VERSION
"""
Streamlined Scholarship model - removed 47 unused fields (62% reduction)
Only includes fields that are actually being used in production
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ScholarshipType(str, Enum):
    """Types of scholarships available"""

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
    """Status of scholarship listings"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"


class DifficultyLevel(str, Enum):
    """Application difficulty levels"""

    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"


class Scholarship(Base):
    """
    Simplified Scholarship model - only fields with actual data
    Removed 47 unused fields for better performance and maintainability
    """

    __tablename__ = "scholarships"

    # ===========================
    # CORE IDENTIFICATION
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    organization = Column(String(255), nullable=False, index=True)

    # ===========================
    # CLASSIFICATION
    # ===========================
    scholarship_type = Column(SQLEnum(ScholarshipType), nullable=False, index=True)
    status = Column(
        SQLEnum(ScholarshipStatus), default=ScholarshipStatus.ACTIVE, nullable=False
    )
    difficulty_level = Column(
        SQLEnum(DifficultyLevel), default=DifficultyLevel.MODERATE, nullable=False
    )

    # ===========================
    # FINANCIAL INFO
    # ===========================
    amount_exact = Column(Integer, nullable=False)
    is_renewable = Column(Boolean, default=False, nullable=False)

    # ===========================
    # ELIGIBILITY FLAGS
    # ===========================
    need_based_required = Column(Boolean, default=False, nullable=False)
    international_students_eligible = Column(Boolean, default=False, nullable=False)
    leadership_required = Column(Boolean, default=False, nullable=False)
    work_experience_required = Column(Boolean, default=False, nullable=False)
    military_affiliation_required = Column(Boolean, default=False, nullable=False)

    # ===========================
    # APPLICATION REQUIREMENTS
    # ===========================
    essay_required = Column(Boolean, default=False, nullable=False)
    transcript_required = Column(Boolean, default=True, nullable=False)
    recommendation_letters_required = Column(Integer, default=0, nullable=False)
    portfolio_required = Column(Boolean, default=False, nullable=False)
    interview_required = Column(Boolean, default=False, nullable=False)

    # Essay type flags
    personal_statement_required = Column(Boolean, default=False, nullable=False)
    leadership_essay_required = Column(Boolean, default=False, nullable=False)
    community_service_essay_required = Column(Boolean, default=False, nullable=False)

    # ===========================
    # DEADLINE INFO
    # ===========================
    is_rolling_deadline = Column(Boolean, default=False, nullable=False)

    # ===========================
    # DISPLAY & BRANDING
    # ===========================
    primary_image_url = Column(String(500), nullable=True)

    # ===========================
    # ADMIN & METRICS
    # ===========================
    verified = Column(Boolean, default=False, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    applications_count = Column(Integer, default=0, nullable=False)

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Scholarship(id={self.id}, title='{self.title}', amount=${self.amount_exact})>"
