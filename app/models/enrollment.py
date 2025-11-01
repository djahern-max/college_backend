# app/models/enrollment.py
"""
SQLAlchemy model for enrollment data (student body composition)
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class EnrollmentData(Base):
    """
    Enrollment statistics by academic year.
    Tracks total enrollment, demographics, and student composition.
    """

    __tablename__ = "enrollment_data"
    __table_args__ = {"comment": "Enrollment statistics by academic year"}

    id = Column(Integer, primary_key=True, index=True)
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

    # Total enrollment
    total_enrollment = Column(
        Integer, nullable=True, index=True, comment="Total undergraduate enrollment"
    )
    full_time_enrollment = Column(
        Integer, nullable=True, comment="Full-time undergraduate enrollment"
    )
    part_time_enrollment = Column(
        Integer, nullable=True, comment="Part-time undergraduate enrollment"
    )

    # Demographics by gender
    enrollment_men = Column(
        Integer, nullable=True, comment="Number of male students enrolled"
    )
    enrollment_women = Column(
        Integer, nullable=True, comment="Number of female students enrolled"
    )

    # Residency
    enrollment_in_state = Column(
        Integer, nullable=True, comment="Number of in-state students"
    )
    enrollment_out_of_state = Column(
        Integer, nullable=True, comment="Number of out-of-state students"
    )

    # Percentages (calculated)
    percent_full_time = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentage of students enrolled full-time",
    )
    percent_in_state = Column(
        Numeric(5, 2), nullable=True, comment="Percentage of students from in-state"
    )

    # Metadata
    created_at = Column(
        DateTime,
        server_default=text("now()"),
        nullable=False,
        comment="Record creation timestamp",
    )
    updated_at = Column(
        DateTime,
        server_default=text("now()"),
        nullable=False,
        comment="Record last update timestamp",
    )

    # Relationships
    institution = relationship("Institution", back_populates="enrollment_data")

    def __repr__(self):
        return f"<EnrollmentData(ipeds_id={self.ipeds_id}, year={self.academic_year}, total={self.total_enrollment})>"
