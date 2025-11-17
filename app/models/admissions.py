# app/models/admissions.py
"""
SQLAlchemy model for admissions data (test scores, acceptance rates, etc.)
UPDATED: Added institution_id and is_admin_verified to align with CampusConnect
FIXED: Specify foreign_keys in relationship to avoid ambiguity
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean,
    text,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class AdmissionsData(Base):
    """
    Admissions statistics and test scores by academic year.
    Tracks acceptance rates, SAT/ACT scores, and application numbers.
    """

    __tablename__ = "admissions_data"
    __table_args__ = {
        "comment": "Admissions statistics and test scores by academic year"
    }

    id = Column(Integer, primary_key=True, index=True)

    # Direct foreign key to institutions table (in addition to ipeds_id)
    institution_id = Column(
        Integer,
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Direct foreign key to institutions.id",
    )

    ipeds_id = Column(
        Integer,
        ForeignKey("institutions.ipeds_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="IPEDS institution identifier",
    )

    academic_year = Column(
        String(10), nullable=False, index=True, comment="Academic year (e.g., 2023-24)"
    )

    # Application numbers
    applications_total = Column(
        Integer, nullable=True, comment="Total applications received"
    )
    admissions_total = Column(Integer, nullable=True, comment="Total students admitted")
    enrolled_total = Column(Integer, nullable=True, comment="Total students enrolled")

    # Calculated rates
    acceptance_rate = Column(
        Numeric(5, 2),
        nullable=True,
        index=True,
        comment="Acceptance rate as percentage (0-100)",
    )
    yield_rate = Column(
        Numeric(5, 2), nullable=True, comment="Yield rate as percentage (0-100)"
    )

    # SAT scores (middle 50%)
    sat_reading_25th = Column(
        Integer,
        nullable=True,
        comment="SAT Evidence-Based Reading/Writing 25th percentile",
    )
    sat_reading_50th = Column(
        Integer,
        nullable=True,
        comment="SAT Evidence-Based Reading/Writing 50th percentile (median)",
    )
    sat_reading_75th = Column(
        Integer,
        nullable=True,
        comment="SAT Evidence-Based Reading/Writing 75th percentile",
    )

    sat_math_25th = Column(Integer, nullable=True, comment="SAT Math 25th percentile")
    sat_math_50th = Column(
        Integer, nullable=True, index=True, comment="SAT Math 50th percentile (median)"
    )
    sat_math_75th = Column(Integer, nullable=True, comment="SAT Math 75th percentile")

    # Test submission percentages
    percent_submitting_sat = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentage of enrolled students who submitted SAT",
    )

    # Admin verification flag (for CampusConnect integration)
    is_admin_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if admin has verified/updated this data via CampusConnect",
    )

    # Metadata
    created_at = Column(
        DateTime,
        server_default=text("now()"),
        nullable=False,
        comment="Record creation timestamp",
    )

    # Relationships - FIXED: Use institution_id as primary relationship
    institution = relationship(
        "Institution",
        back_populates="admissions_data",
        foreign_keys=[institution_id],  # FIXED: Specify which FK to use
    )

    def __repr__(self):
        return f"<AdmissionsData(ipeds_id={self.ipeds_id}, year={self.academic_year})>"
