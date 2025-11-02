# app/models/institution.py
"""
UPDATED Institution model - added IPEDS enrichment fields
Added: student_faculty_ratio, size_category, locale
Added: relationships to admissions_data, enrollment_data, graduation_data
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from typing import List, Optional


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "PUBLIC"
    PRIVATE_NONPROFIT = "PRIVATE_NONPROFIT"
    PRIVATE_FOR_PROFIT = "PRIVATE_FOR_PROFIT"


class Institution(Base):
    """
    Institution model with IPEDS enrichment data
    Core fields + static characteristics + relationships to time-series data
    """

    __tablename__ = "institutions"

    # ===========================
    # CORE IDENTIFICATION
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)

    # ===========================
    # LOCATION
    # ===========================
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)

    # ===========================
    # CLASSIFICATION
    # ===========================
    control_type = Column(SQLEnum(ControlType), nullable=False, index=True)

    # ===========================
    # DISPLAY & BRANDING
    # ===========================
    primary_image_url = Column(String(500), nullable=True)

    # ===========================
    # NEW: STATIC INSTITUTIONAL CHARACTERISTICS
    # ===========================
    student_faculty_ratio = Column(
        Numeric(5, 2),
        nullable=True,
        index=True,
        comment="Student to faculty ratio (e.g., 17.00 for 17:1)",
    )

    size_category = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Institution size: Small (<2k), Medium (2k-10k), Large (10k-20k), Very Large (20k+)",
    )

    locale = Column(
        String(50),
        nullable=True,
        comment="Urbanization level: City, Suburban, Town, Rural",
    )

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ===========================
    # RELATIONSHIPS
    # ===========================

    # Existing relationship
    tuition_data = relationship(
        "TuitionData", back_populates="institution", cascade="all, delete-orphan"
    )

    # NEW: Relationships to enrichment data tables
    admissions_data = relationship(
        "AdmissionsData",
        back_populates="institution",
        cascade="all, delete-orphan",
        order_by="AdmissionsData.academic_year.desc()",
        lazy="select",  # Only load when explicitly accessed
    )

    enrollment_data = relationship(
        "EnrollmentData",
        back_populates="institution",
        cascade="all, delete-orphan",
        order_by="EnrollmentData.academic_year.desc()",
        lazy="select",
    )

    graduation_data = relationship(
        "GraduationData",
        back_populates="institution",
        cascade="all, delete-orphan",
        order_by="GraduationData.cohort_year.desc()",
        lazy="select",
    )

    # ===========================
    # COMPUTED PROPERTIES
    # ===========================
    @property
    def display_name(self) -> str:
        """Return name with location for display"""
        return f"{self.name} ({self.city}, {self.state})"

    @property
    def is_public(self) -> bool:
        """Check if institution is public"""
        return self.control_type == ControlType.PUBLIC

    @property
    def is_private(self) -> bool:
        """Check if institution is private"""
        return self.control_type in [
            ControlType.PRIVATE_NONPROFIT,
            ControlType.PRIVATE_FOR_PROFIT,
        ]

    # NEW: Convenience properties for latest data
    @property
    def latest_admissions(self):
        """Get most recent admissions data"""
        return self.admissions_data[0] if self.admissions_data else None

    @property
    def latest_enrollment(self):
        """Get most recent enrollment data"""
        return self.enrollment_data[0] if self.enrollment_data else None

    @property
    def latest_graduation(self):
        """Get most recent graduation data"""
        return self.graduation_data[0] if self.graduation_data else None

    # ===========================
    # CLASS METHODS FOR QUERIES
    # ===========================
    @classmethod
    def get_by_state(
        cls, db: Session, state: str, limit: int = 50
    ) -> List["Institution"]:
        """Get institutions by state"""
        return (
            db.query(cls)
            .filter(cls.state == state)
            .order_by(cls.name)
            .limit(limit)
            .all()
        )

    @classmethod
    def get_by_size(
        cls, db: Session, size_category: str, limit: int = 50
    ) -> List["Institution"]:
        """Get institutions by"""
        return (
            db.query(cls)
            .filter(cls.size_category == size_category)
            .order_by(cls.name)
            .limit(limit)
            .all()
        )

    # ===========================
    # TABLE INDEXES
    # ===========================
    __table_args__ = (
        Index("idx_institution_state_city", "state", "city"),
        # Indexes on new columns are created via Column definition
    )

    def __repr__(self):
        return f"<Institution(id={self.id}, name='{self.name}', state='{self.state}')>"


# ===========================
# MIGRATION NOTE
# ===========================
"""
After updating this file, run:
1. alembic revision --autogenerate -m "add ipeds enrichment fields"
2. alembic upgrade head

Or use the provided migration file: add_ipeds_enrichment_data.py
"""
