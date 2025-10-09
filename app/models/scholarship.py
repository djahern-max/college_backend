# app/models/scholarship.py - TRULY SIMPLIFIED
"""
Simplified Scholarship model - removes excessive boolean flags
Only keeps essential fields
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
    """Types of scholarships - matches UI filter categories"""

    ACADEMIC_MERIT = "academic_merit"  # 🎓 GPA/grades based
    NEED_BASED = "need_based"  # 💵 Income/financial need
    STEM = "stem"  # 🔬 Science, tech, engineering, math
    ARTS = "arts"  # 🎨 Creative fields
    DIVERSITY = "diversity"  # 🌈 Underrepresented groups
    ATHLETIC = "athletic"  # ⚽ Sports scholarships
    LEADERSHIP = "leadership"  # 👥 Leadership/community service
    MILITARY = "military"  # 🎖️ Military families
    CAREER_SPECIFIC = "career_specific"  # 💼 Specific career fields
    OTHER = "other"  # Anything else


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
    Simplified Scholarship model - removed boolean flags for easier maintenance
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
    # IMAGES
    # ===========================
    primary_image_url = Column(String(500))

    # ===========================
    # METADATA
    # ===========================
    verified = Column(Boolean, default=False, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    applications_count = Column(Integer, default=0, nullable=False)

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Scholarship {self.id}: {self.title}>"
