# app/models/step2_ic2023_ay.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional


class Step2_IC2023_AY(Base):
    """
    Step 2: Financial Data from IC2023_AY
    Tuition, fees, room & board, and related costs
    """

    __tablename__ = "step2_ic2023_ay"

    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(
        Integer, ForeignKey("institutions.ipeds_id"), nullable=False, index=True
    )

    academic_year = Column(String(10), nullable=False, default="2023-24")
    data_source = Column(String(50), nullable=False, default="IC2023_AY")

    tuition_in_state = Column(Float, nullable=True)
    tuition_out_state = Column(Float, nullable=True)
    required_fees = Column(Float, nullable=True)
    tuition_fees_in_state = Column(Float, nullable=True)
    tuition_fees_out_state = Column(Float, nullable=True)
    room_board_on_campus = Column(Float, nullable=True)
    room_board_off_campus = Column(Float, nullable=True)
    books_supplies = Column(Float, nullable=True)
    personal_expenses = Column(Float, nullable=True)
    transportation = Column(Float, nullable=True)

    has_tuition_data = Column(Boolean, default=False)
    has_fees_data = Column(Boolean, default=False)
    data_completeness_score = Column(Integer, default=0)
    validation_issues = Column(Text, nullable=True)
    validation_status = Column(String(20), default="pending")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    institution = relationship("Institution", back_populates="step2_financial_data")

    def __repr__(self):
        return f"<Step2_IC2023_AY(ipeds_id={self.ipeds_id}, tuition_in_state={self.tuition_in_state})>"

    @property
    def total_cost_in_state(self) -> Optional[float]:
        costs = [
            self.tuition_fees_in_state or self.tuition_in_state,
            self.required_fees,
            self.room_board_on_campus,
            self.books_supplies,
            self.personal_expenses,
            self.transportation,
        ]
        valid_costs = [cost for cost in costs if cost is not None]
        return sum(valid_costs) if valid_costs else None

    @property
    def total_cost_out_state(self) -> Optional[float]:
        costs = [
            self.tuition_fees_out_state or self.tuition_out_state,
            self.required_fees,
            self.room_board_on_campus,
            self.books_supplies,
            self.personal_expenses,
            self.transportation,
        ]
        valid_costs = [cost for cost in costs if cost is not None]
        return sum(valid_costs) if valid_costs else None

    @property
    def has_comprehensive_data(self) -> bool:
        return (
            self.tuition_in_state is not None
            and self.tuition_out_state is not None
            and self.room_board_on_campus is not None
        )

    def to_dict(self) -> dict:
        """Convert model instance to dictionary for API responses"""

        # Create cost breakdown for display
        cost_breakdown = {
            "tuition_in_state": self.tuition_in_state,
            "tuition_out_state": self.tuition_out_state,
            "required_fees": self.required_fees,
            "tuition_fees_in_state": self.tuition_fees_in_state,
            "tuition_fees_out_state": self.tuition_fees_out_state,
            "room_board_on_campus": self.room_board_on_campus,
            "room_board_off_campus": self.room_board_off_campus,
            "books_supplies": self.books_supplies,
            "personal_expenses": self.personal_expenses,
            "transportation": self.transportation,
        }

        return {
            "id": self.id,
            "ipeds_id": self.ipeds_id,
            "academic_year": self.academic_year,
            "data_source": self.data_source,
            "tuition_in_state": self.tuition_in_state,
            "tuition_out_state": self.tuition_out_state,
            "required_fees": self.required_fees,
            "tuition_fees_in_state": self.tuition_fees_in_state,
            "tuition_fees_out_state": self.tuition_fees_out_state,
            "room_board_on_campus": self.room_board_on_campus,
            "room_board_off_campus": self.room_board_off_campus,
            "books_supplies": self.books_supplies,
            "personal_expenses": self.personal_expenses,
            "transportation": self.transportation,
            "total_cost_in_state": self.total_cost_in_state,
            "total_cost_out_state": self.total_cost_out_state,
            "has_tuition_data": self.has_tuition_data,
            "has_fees_data": self.has_fees_data,
            "data_completeness_score": self.data_completeness_score,
            "validation_status": self.validation_status,
            "has_comprehensive_data": self.has_comprehensive_data,
            "cost_breakdown": cost_breakdown,  # Added this field
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
