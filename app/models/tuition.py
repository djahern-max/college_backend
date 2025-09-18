# app/models/tuition.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional


class TuitionData(Base):
    """
    Enhanced Tuition Data from IPEDS IC2023_AY
    Tuition, fees, room & board, and related costs with projections support
    """

    __tablename__ = "tuition_data"

    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(
        Integer, ForeignKey("institutions.ipeds_id"), nullable=False, index=True
    )

    # Data source information
    academic_year = Column(String(10), nullable=False, default="2023-24")
    data_source = Column(String(50), nullable=False, default="IC2023_AY")

    # Tuition data
    tuition_in_state = Column(Float, nullable=True)
    tuition_out_state = Column(Float, nullable=True)

    # Fees data - separate for in-state and out-of-state
    required_fees_in_state = Column(Float, nullable=True)
    required_fees_out_state = Column(Float, nullable=True)

    # Combined tuition + fees
    tuition_fees_in_state = Column(Float, nullable=True)
    tuition_fees_out_state = Column(Float, nullable=True)

    # Living expenses
    room_board_on_campus = Column(Float, nullable=True)
    room_board_off_campus = Column(Float, nullable=True)
    books_supplies = Column(Float, nullable=True)
    personal_expenses = Column(Float, nullable=True)
    transportation = Column(Float, nullable=True)

    # Data quality indicators
    has_tuition_data = Column(Boolean, default=False)
    has_fees_data = Column(Boolean, default=False)
    has_living_data = Column(Boolean, default=False)  # New field from CSV
    data_completeness_score = Column(Integer, default=0)
    validation_status = Column(String(20), default="pending")

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    institution = relationship("Institution", back_populates="tuition_data")

    def __repr__(self):
        return f"<TuitionData(ipeds_id={self.ipeds_id}, tuition_in_state={self.tuition_in_state})>"

    @property
    def total_cost_in_state(self) -> Optional[float]:
        """Calculate total cost of attendance for in-state students"""
        costs = [
            self.tuition_fees_in_state,
            self.room_board_on_campus,
            self.books_supplies,
            self.personal_expenses,
            self.transportation,
        ]
        valid_costs = [cost for cost in costs if cost is not None]
        return sum(valid_costs) if valid_costs else None

    @property
    def total_cost_out_state(self) -> Optional[float]:
        """Calculate total cost of attendance for out-of-state students"""
        costs = [
            self.tuition_fees_out_state,
            self.room_board_on_campus,
            self.books_supplies,
            self.personal_expenses,
            self.transportation,
        ]
        valid_costs = [cost for cost in costs if cost is not None]
        return sum(valid_costs) if valid_costs else None

    @property
    def has_comprehensive_data(self) -> bool:
        """Check if we have comprehensive cost data"""
        return (
            self.tuition_in_state is not None
            and self.tuition_out_state is not None
            and self.room_board_on_campus is not None
            and self.has_living_data
        )

    @property
    def affordability_category(self) -> str:
        """Categorize institution by affordability based on in-state tuition"""
        if not self.tuition_in_state:
            return "unknown"

        tuition = self.tuition_in_state
        if tuition <= 5000:
            return "very_affordable"
        elif tuition <= 15000:
            return "affordable"
        elif tuition <= 30000:
            return "moderate"
        elif tuition <= 50000:
            return "expensive"
        else:
            return "very_expensive"

    def calculate_projected_costs(
        self, years: int = 4, inflation_rate: float = 0.04
    ) -> dict:
        """Calculate projected costs for future years"""
        if not self.tuition_in_state:
            return {}

        projections = []
        current_year = 2023

        for year in range(1, years + 1):
            multiplier = (1 + inflation_rate) ** year

            projection = {
                "year": f"{current_year + year}-{str(current_year + year + 1)[2:]}",
                "tuition_in_state": (
                    round(self.tuition_in_state * multiplier, 2)
                    if self.tuition_in_state
                    else None
                ),
                "tuition_out_state": (
                    round(self.tuition_out_state * multiplier, 2)
                    if self.tuition_out_state
                    else None
                ),
                "total_cost_in_state": (
                    round(self.total_cost_in_state * multiplier, 2)
                    if self.total_cost_in_state
                    else None
                ),
                "total_cost_out_state": (
                    round(self.total_cost_out_state * multiplier, 2)
                    if self.total_cost_out_state
                    else None
                ),
                "inflation_rate": inflation_rate,
            }
            projections.append(projection)

        return {"projections": projections}

    def analyze_affordability(
        self, household_income: float, residency: str = "in_state"
    ) -> dict:
        """Analyze affordability for a given household income"""
        max_recommended = household_income * 0.10  # 10% rule

        current_cost = (
            self.total_cost_in_state
            if residency == "in_state"
            else self.total_cost_out_state
        )

        if not current_cost:
            return {"error": "Insufficient cost data for analysis"}

        return {
            "household_income": household_income,
            "max_recommended_cost": round(max_recommended, 2),
            "current_total_cost": round(current_cost, 2),
            "is_affordable": current_cost <= max_recommended,
            "percentage_of_income": round((current_cost / household_income) * 100, 1),
            "over_budget_amount": max(0, round(current_cost - max_recommended, 2)),
        }

    def to_dict(self) -> dict:
        """Convert model instance to dictionary for API responses"""

        # Create detailed cost breakdown
        cost_breakdown = {
            "tuition_in_state": self.tuition_in_state,
            "tuition_out_state": self.tuition_out_state,
            "required_fees_in_state": self.required_fees_in_state,
            "required_fees_out_state": self.required_fees_out_state,
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
            # Individual cost components
            "tuition_in_state": self.tuition_in_state,
            "tuition_out_state": self.tuition_out_state,
            "required_fees_in_state": self.required_fees_in_state,
            "required_fees_out_state": self.required_fees_out_state,
            "tuition_fees_in_state": self.tuition_fees_in_state,
            "tuition_fees_out_state": self.tuition_fees_out_state,
            "room_board_on_campus": self.room_board_on_campus,
            "room_board_off_campus": self.room_board_off_campus,
            "books_supplies": self.books_supplies,
            "personal_expenses": self.personal_expenses,
            "transportation": self.transportation,
            # Calculated fields
            "total_cost_in_state": self.total_cost_in_state,
            "total_cost_out_state": self.total_cost_out_state,
            "affordability_category": self.affordability_category,
            # Data quality indicators
            "has_tuition_data": self.has_tuition_data,
            "has_fees_data": self.has_fees_data,
            "has_living_data": self.has_living_data,
            "has_comprehensive_data": self.has_comprehensive_data,
            "data_completeness_score": self.data_completeness_score,
            "validation_status": self.validation_status,
            # Detailed breakdown for frontend
            "cost_breakdown": cost_breakdown,
            # Timestamps
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
