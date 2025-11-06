# app/models/scholarship.py - SIMPLIFIED WITH ESSENTIAL FIELDS
"""
Simplified Scholarship model with essential fields only
Focuses on practical information needed for scholarship search
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from sqlalchemy.orm import relationship


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
    Simplified Scholarship model with essential practical fields
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
    # Use amount_min/amount_max for ranges, or set them equal for exact amounts
    amount_min = Column(Integer, nullable=False)  # Minimum award amount
    amount_max = Column(Integer, nullable=False)  # Maximum award amount
    is_renewable = Column(Boolean, default=False, nullable=False)
    number_of_awards = Column(Integer, nullable=True)  # How many scholarships available

    # ===========================
    # DATES
    # ===========================
    deadline = Column(Date, nullable=True, index=True)  # Application deadline
    application_opens = Column(Date, nullable=True)  # When applications open
    for_academic_year = Column(String(20), nullable=True)  # e.g., "2027-2028"

    # ===========================
    # DETAILS
    # ===========================
    description = Column(String(500), nullable=True)  # 2-3 sentences MAX
    website_url = Column(String(500), nullable=True)

    # ===========================
    # REQUIREMENTS
    # ===========================
    min_gpa = Column(Numeric(3, 2), nullable=True)  # e.g., 3.50

    # ===========================
    # IMAGES
    # ===========================
    primary_image_url = Column(String(500), nullable=True)

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

    applications = relationship("ScholarshipApplication", back_populates="scholarship")

    def __repr__(self):
        return f"<Scholarship(id={self.id}, title='{self.title}', amount=${self.amount_min}-${self.amount_max})>"

    @property
    def amount_display(self) -> str:
        """Return formatted amount string for display"""
        if self.amount_min == self.amount_max:
            return f"${self.amount_min:,}"
        return f"${self.amount_min:,} - ${self.amount_max:,}"
