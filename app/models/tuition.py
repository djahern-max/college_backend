# app/models/tuition.py
"""
Complete TuitionData model for PostgreSQL with all fields from CSV
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
from datetime import datetime


class ValidationStatus(PyEnum):
    """Data validation status enum"""

    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED = "FAILED"


class TuitionData(Base):
    """
    Complete Tuition Data model matching magicscholar_financial_data.csv
    Includes all financial data with quality indicators and validation
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
        default="2023-24",
        index=True,
        comment='Academic year (e.g., "2023-24")',
    )
    data_source = Column(
        String(500),
        nullable=False,
        default="IPEDS",
        index=True,
        comment='Source of the data (e.g., "IPEDS", "Manual", "School Website)',
    )

    # Core tuition fields
    tuition_in_state = Column(
        Float, nullable=True, index=True, comment="In-state tuition cost"
    )
    tuition_out_state = Column(
        Float, nullable=True, index=True, comment="Out-of-state tuition cost"
    )

    # Fee fields - separated for in-state and out-of-state
    required_fees_in_state = Column(
        Float, nullable=True, comment="Required fees for in-state students"
    )
    required_fees_out_state = Column(
        Float, nullable=True, comment="Required fees for out-of-state students"
    )

    # Combined tuition + fees (calculated or direct from source)
    tuition_fees_in_state = Column(
        Float, nullable=True, index=True, comment="Total tuition + fees for in-state"
    )
    tuition_fees_out_state = Column(
        Float,
        nullable=True,
        index=True,
        comment="Total tuition + fees for out-of-state",
    )

    # Living expenses
    room_board_on_campus = Column(
        Float, nullable=True, comment="Room and board costs on campus"
    )

    # Data quality and validation fields
    has_tuition_data = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether tuition data is available",
    )
    has_fees_data = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether fee data is available",
    )
    has_living_data = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether living expense data is available",
    )
    data_completeness_score = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="Data completeness score (0-100)",
    )
    validation_status = Column(
        Enum(ValidationStatus),
        nullable=False,
        default=ValidationStatus.PENDING,
        index=True,
        comment="Data validation status",
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
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, PyEnum):
                value = value.value
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value

        # Add calculated fields
        result.update(self._get_calculated_fields())
        return result

    def _get_calculated_fields(self) -> Dict[str, Any]:
        """Calculate derived fields for API responses"""
        # Calculate total costs
        total_cost_in_state = None
        total_cost_out_state = None

        if self.tuition_fees_in_state:
            base_cost = self.tuition_fees_in_state
            additional_costs = self.room_board_on_campus or 0
            total_cost_in_state = base_cost + additional_costs

        if self.tuition_fees_out_state:
            base_cost = self.tuition_fees_out_state
            additional_costs = self.room_board_on_campus or 0
            total_cost_out_state = base_cost + additional_costs

        # Determine affordability category
        affordability_category = self._get_affordability_category()

        # Check if comprehensive data available
        has_comprehensive_data = (
            self.has_tuition_data
            and self.has_fees_data
            and self.has_living_data
            and self.data_completeness_score >= 80
        )

        return {
            "total_cost_in_state": total_cost_in_state,
            "total_cost_out_state": total_cost_out_state,
            "affordability_category": affordability_category,
            "has_comprehensive_data": has_comprehensive_data,
            "cost_breakdown": {
                "tuition_in_state": self.tuition_in_state,
                "tuition_out_state": self.tuition_out_state,
                "required_fees_in_state": self.required_fees_in_state,
                "required_fees_out_state": self.required_fees_out_state,
                "tuition_fees_in_state": self.tuition_fees_in_state,
                "tuition_fees_out_state": self.tuition_fees_out_state,
                "room_board_on_campus": self.room_board_on_campus,
            },
        }

    def _get_affordability_category(self) -> str:
        """Determine affordability category based on in-state tuition"""
        if not self.tuition_in_state:
            return "UNKNOWN"

        tuition = self.tuition_in_state
        if tuition < 10000:
            return "VERY_AFFORDABLE"
        elif tuition < 25000:
            return "AFFORDABLE"
        elif tuition < 40000:
            return "MODERATE"
        elif tuition < 55000:
            return "EXPENSIVE"
        else:
            return "VERY_EXPENSIVE"

    def __repr__(self) -> str:
        return f"<TuitionData(ipeds_id={self.ipeds_id}, academic_year='{self.academic_year}', completeness={self.data_completeness_score}%)>"
