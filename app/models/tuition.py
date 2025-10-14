# app/models/tuition.py
"""
Simplified TuitionData model for PostgreSQL
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Dict, Any
from datetime import datetime


class TuitionData(Base):
    """
    Simplified Tuition Data model with only essential fields
    """

    __tablename__ = "tuition_data"

    # Primary key and foreign key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key")
    ipeds_id = Column(
        Integer,
        ForeignKey("institutions.ipeds_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Institution IPEDS ID (foreign key)",
    )

    # Data source information
    academic_year = Column(
        String(10),
        nullable=False,
        default="2025-26",
        index=True,
        comment='Academic year (e.g., "2025-26")',
    )
    data_source = Column(
        String(500),
        nullable=False,
        index=True,
        comment='Source of the data (e.g., "https://...")',
    )

    # Core tuition fields
    tuition_in_state = Column(
        Float, nullable=True, index=True, comment="In-state tuition cost"
    )
    tuition_out_state = Column(
        Float, nullable=True, index=True, comment="Out-of-state tuition cost"
    )

    # Fee fields
    required_fees_in_state = Column(
        Float, nullable=True, comment="Required fees for in-state students"
    )
    required_fees_out_state = Column(
        Float, nullable=True, comment="Required fees for out-of-state students"
    )

    # Living expenses
    room_board_on_campus = Column(
        Float, nullable=True, comment="Room and board costs on campus"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp",
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp",
    )

    # Relationships
    institution = relationship("Institution", back_populates="tuition_data")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "ipeds_id",
            "academic_year",
            "data_source",
            name="uq_tuition_institution_year_source",
        ),
        {"comment": "Tuition and financial data for institutions"},
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "ipeds_id": self.ipeds_id,
            "academic_year": self.academic_year,
            "data_source": self.data_source,
            "tuition_in_state": self.tuition_in_state,
            "tuition_out_state": self.tuition_out_state,
            "required_fees_in_state": self.required_fees_in_state,
            "required_fees_out_state": self.required_fees_out_state,
            "room_board_on_campus": self.room_board_on_campus,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<TuitionData(ipeds_id={self.ipeds_id}, academic_year='{self.academic_year}')>"
