# app/models/institution.py
"""
UPDATED Institution model - denormalized with tuition data in same table
No separate TuitionData relationship needed
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Enum as SQLEnum,
    Boolean,
    SmallInteger,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "PUBLIC"
    PRIVATE_NONPROFIT = "PRIVATE_NONPROFIT"
    PRIVATE_FOR_PROFIT = "PRIVATE_FOR_PROFIT"


class Institution(Base):
    """
    Institution model with denormalized data.
    All tuition, cost, and admissions data stored directly in this table.
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
    level = Column(SmallInteger, nullable=True)
    control = Column(SmallInteger, nullable=True)

    # ===========================
    # DISPLAY & BRANDING
    # ===========================
    primary_image_url = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True, index=True)
    is_featured = Column(Boolean, nullable=False, default=False, index=True)

    # ===========================
    # STATIC CHARACTERISTICS
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
        comment="Small (<2k), Medium (2k-10k), Large (10k-20k), Very Large (20k+)",
    )
    locale = Column(
        String(50),
        nullable=True,
        comment="Urbanization level: City, Suburban, Town, Rural",
    )

    # ===========================
    # TUITION & COSTS (DENORMALIZED)
    # ===========================
    tuition_in_state = Column(Numeric(10, 2), nullable=True)
    tuition_out_of_state = Column(Numeric(10, 2), nullable=True)
    tuition_private = Column(Numeric(10, 2), nullable=True)
    tuition_in_district = Column(Numeric(10, 2), nullable=True)

    room_cost = Column(Numeric(10, 2), nullable=True)
    board_cost = Column(Numeric(10, 2), nullable=True)
    room_and_board = Column(Numeric(10, 2), nullable=True)

    application_fee_undergrad = Column(Numeric(10, 2), nullable=True)
    application_fee_grad = Column(Numeric(10, 2), nullable=True)

    # ===========================
    # ADMISSIONS DATA (DENORMALIZED)
    # ===========================
    acceptance_rate = Column(Numeric(5, 2), nullable=True)

    # SAT scores
    sat_reading_25th = Column(SmallInteger, nullable=True)
    sat_reading_75th = Column(SmallInteger, nullable=True)
    sat_math_25th = Column(SmallInteger, nullable=True)
    sat_math_75th = Column(SmallInteger, nullable=True)

    # ACT scores
    act_composite_25th = Column(SmallInteger, nullable=True)
    act_composite_75th = Column(SmallInteger, nullable=True)

    # ===========================
    # DATA QUALITY & VERIFICATION
    # ===========================
    data_completeness_score = Column(Integer, nullable=False, default=0, index=True)
    completeness_score = Column(Integer, nullable=False, default=0)

    admin_verified = Column(Boolean, nullable=False, default=False, index=True)
    cost_data_verified = Column(Boolean, nullable=False, default=False)
    cost_data_verified_at = Column(DateTime(timezone=True), nullable=True)
    admissions_data_verified = Column(Boolean, nullable=False, default=False)
    admissions_data_verified_at = Column(DateTime(timezone=True), nullable=True)

    last_admin_update = Column(DateTime(timezone=True), nullable=True)
    data_quality_notes = Column(String(500), nullable=True)

    # ===========================
    # DATA SOURCE TRACKING
    # ===========================
    data_last_updated = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    data_source = Column(
        String(50),
        nullable=False,
        default="ipeds",
        index=True,
    )
    ipeds_year = Column(
        String(10),
        nullable=True,
        default="2023-24",
    )

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ===========================
    # RELATIONSHIPS (OPTIONAL - if you still have enrollment/graduation tables)
    # ===========================
    # Only include these if you still have separate enrollment_data and graduation_data tables
    # If those are also denormalized, remove these relationships

    # enrollment_data = relationship(
    #     "EnrollmentData",
    #     back_populates="institution",
    #     cascade="all, delete-orphan",
    # )
    #
    # graduation_data = relationship(
    #     "GraduationData",
    #     back_populates="institution",
    #     cascade="all, delete-orphan",
    # )

    def __repr__(self):
        return (
            f"<Institution(id={self.id}, ipeds_id={self.ipeds_id}, name='{self.name}')>"
        )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "ipeds_id": self.ipeds_id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "control_type": self.control_type.value if self.control_type else None,
            "website": self.website,
            "primary_image_url": self.primary_image_url,
            "is_featured": self.is_featured,
            "tuition_in_state": (
                float(self.tuition_in_state) if self.tuition_in_state else None
            ),
            "tuition_out_of_state": (
                float(self.tuition_out_of_state) if self.tuition_out_of_state else None
            ),
            "room_and_board": (
                float(self.room_and_board) if self.room_and_board else None
            ),
            "acceptance_rate": (
                float(self.acceptance_rate) if self.acceptance_rate else None
            ),
            "data_completeness_score": self.data_completeness_score,
        }
