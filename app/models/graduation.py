# app/models/graduation.py
"""
SQLAlchemy model for graduation and retention data
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class GraduationData(Base):
    """
    Graduation and retention rates by cohort year.
    Tracks how well institutions retain and graduate students.
    """

    __tablename__ = "graduation_data"
    __table_args__ = {"comment": "Graduation and retention rates by cohort year"}

    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(
        Integer,
        ForeignKey("institutions.ipeds_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="IPEDS institution identifier",
    )
    cohort_year = Column(
        String(10),
        nullable=False,
        index=True,
        comment="Starting cohort year (e.g., 2017 for 6-year rate in 2023)",
    )

    # Retention
    retention_rate = Column(
        Numeric(5, 2),
        nullable=True,
        index=True,
        comment="First-year retention rate (percentage)",
    )

    # Graduation rates
    graduation_rate_4_year = Column(
        Numeric(5, 2), nullable=True, comment="4-year graduation rate (percentage)"
    )
    graduation_rate_6_year = Column(
        Numeric(5, 2),
        nullable=True,
        index=True,
        comment="6-year graduation rate (percentage)",
    )
    graduation_rate_8_year = Column(
        Numeric(5, 2), nullable=True, comment="8-year graduation rate (percentage)"
    )

    # Cohort information
    cohort_size = Column(Integer, nullable=True, comment="Size of the entering cohort")

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
    institution = relationship("Institution", back_populates="graduation_data")

    def __repr__(self):
        return f"<GraduationData(ipeds_id={self.ipeds_id}, cohort={self.cohort_year}, 6yr={self.graduation_rate_6_year})>"
