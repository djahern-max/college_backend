# app/models/tuition.py
"""
Simplified TuitionData model for PostgreSQL
UPDATED: Use Numeric instead of Float to match CampusConnect exactly
FIXED: Specify foreign_keys in relationship to avoid ambiguity
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Boolean,
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

    # Primary key and foreign keys
    id = Column(Integer, primary_key=True, index=True, comment="Primary key")

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

    # Core tuition fields - Using Numeric(10,2) to match CampusConnect
    tuition_in_state = Column(
        Numeric(10, 2), nullable=True, index=True, comment="In-state tuition cost"
    )
    tuition_out_state = Column(
        Numeric(10, 2), nullable=True, index=True, comment="Out-of-state tuition cost"
    )

    # Fee fields
    required_fees_in_state = Column(
        Numeric(10, 2), nullable=True, comment="Required fees for in-state students"
    )
    required_fees_out_state = Column(
        Numeric(10, 2), nullable=True, comment="Required fees for out-of-state students"
    )

    # Living expenses
    room_board_on_campus = Column(
        Numeric(10, 2), nullable=True, comment="Room and board costs on campus"
    )

    # Admin verification flag (for CampusConnect integration)
    is_admin_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if admin has verified/updated this data via CampusConnect",
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

    # Relationships - FIXED: Use institution_id as primary relationship
    institution = relationship(
        "Institution",
        back_populates="tuition_data",
        foreign_keys=[institution_id],  # FIXED: Specify which FK to use
    )

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
            "institution_id": self.institution_id,
            "ipeds_id": self.ipeds_id,
            "academic_year": self.academic_year,
            "data_source": self.data_source,
            "tuition_in_state": (
                float(self.tuition_in_state) if self.tuition_in_state else None
            ),
            "tuition_out_state": (
                float(self.tuition_out_state) if self.tuition_out_state else None
            ),
            "required_fees_in_state": (
                float(self.required_fees_in_state)
                if self.required_fees_in_state
                else None
            ),
            "required_fees_out_state": (
                float(self.required_fees_out_state)
                if self.required_fees_out_state
                else None
            ),
            "room_board_on_campus": (
                float(self.room_board_on_campus) if self.room_board_on_campus else None
            ),
            "is_admin_verified": self.is_admin_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<TuitionData(ipeds_id={self.ipeds_id}, academic_year='{self.academic_year}')>"
