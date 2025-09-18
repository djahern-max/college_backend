# app/services/tuition.py
"""
Complete Tuition Service - Business logic for tuition projections and analysis
Integrates with your existing MagicScholar service architecture
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging
import numpy as np

from app.models.tuition import TuitionData
from app.models.institution import Institution
from app.schemas.tuition import (
    TuitionDataCreate,
    TuitionDataUpdate,
    TuitionSearchFilters,
    AffordabilityRequest,
    ProjectionRequest,
    AffordabilityCategory,
    ValidationStatus,
)

logger = logging.getLogger(__name__)


class TuitionService:
    """Service class for tuition data operations and business logic"""

    def __init__(self, db: Session):
        self.db = db

    # Basic CRUD Operations
    def get_by_ipeds_id(self, ipeds_id: int) -> Optional[TuitionData]:
        """Get tuition data by institution IPEDS ID"""
        return (
            self.db.query(TuitionData).filter(TuitionData.ipeds_id == ipeds_id).first()
        )

    def get_by_id(self, tuition_id: int) -> Optional[TuitionData]:
        """Get tuition data by database ID"""
        return self.db.query(TuitionData).filter(TuitionData.id == tuition_id).first()

    def create(self, tuition_data: TuitionDataCreate) -> TuitionData:
        """Create new tuition data record"""
        db_tuition = TuitionData(**tuition_data.model_dump())

        # Calculate data quality scores
        self._update_data_quality_indicators(db_tuition)

        self.db.add(db_tuition)
        self.db.commit()
        self.db.refresh(db_tuition)

        logger.info(f"Created tuition data for IPEDS {db_tuition.ipeds_id}")
        return db_tuition

    def update(
        self, ipeds_id: int, update_data: TuitionDataUpdate
    ) -> Optional[TuitionData]:
        """Update tuition data"""
        db_tuition = self.get_by_ipeds_id(ipeds_id)
        if not db_tuition:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_tuition, field, value)

        # Recalculate data quality indicators
        self._update_data_quality_indicators(db_tuition)

        self.db.commit()
        self.db.refresh(db_tuition)

        logger.info(f"Updated tuition data for IPEDS {ipeds_id}")
        return db_tuition

    def delete(self, ipeds_id: int) -> bool:
        """Delete tuition data"""
        db_tuition = self.get_by_ipeds_id(ipeds_id)
        if not db_tuition:
            return False

        self.db.delete(db_tuition)
        self.db.commit()
        logger.info(f"Deleted tuition data for IPEDS {ipeds_id}")
        return True

    def bulk_create(self, tuition_records: List[TuitionDataCreate]) -> int:
        """Bulk create tuition data records"""
        db_tuitions = []
        for record in tuition_records:
            db_tuition = TuitionData(**record.model_dump())
            self._update_data_quality_indicators(db_tuition)
            db_tuitions.append(db_tuition)

        self.db.add_all(db_tuitions)
        self.db.commit()

        logger.info(f"Bulk created {len(db_tuitions)} tuition records")
        return len(db_tuitions)

    # Search and Filter Operations
    def search_institutions(
        self, filters: TuitionSearchFilters, limit: int = 50, offset: int = 0
    ) -> Tuple[List[TuitionData], int]:
        """Search institutions with tuition data"""
        query = self.db.query(TuitionData).join(
            Institution, TuitionData.ipeds_id == Institution.ipeds_id
        )

        # Apply filters
        conditions = []

        if filters.min_tuition_in_state is not None:
            conditions.append(
                TuitionData.tuition_in_state >= filters.min_tuition_in_state
            )
        if filters.max_tuition_in_state is not None:
            conditions.append(
                TuitionData.tuition_in_state <= filters.max_tuition_in_state
            )
        if filters.min_tuition_out_state is not None:
            conditions.append(
                TuitionData.tuition_out_state >= filters.min_tuition_out_state
            )
        if filters.max_tuition_out_state is not None:
            conditions.append(
                TuitionData.tuition_out_state <= filters.max_tuition_out_state
            )

        if filters.min_total_cost is not None:
            conditions.append(
                TuitionData.tuition_fees_in_state >= filters.min_total_cost
            )
        if filters.max_total_cost is not None:
            conditions.append(
                TuitionData.tuition_fees_in_state <= filters.max_total_cost
            )

        if filters.affordability_category is not None:
            # Calculate affordability based on tuition ranges
            if filters.affordability_category == AffordabilityCategory.VERY_AFFORDABLE:
                conditions.append(TuitionData.tuition_in_state < 10000)
            elif filters.affordability_category == AffordabilityCategory.AFFORDABLE:
                conditions.append(
                    and_(
                        TuitionData.tuition_in_state >= 10000,
                        TuitionData.tuition_in_state < 25000,
                    )
                )
            elif filters.affordability_category == AffordabilityCategory.MODERATE:
                conditions.append(
                    and_(
                        TuitionData.tuition_in_state >= 25000,
                        TuitionData.tuition_in_state < 40000,
                    )
                )
            elif filters.affordability_category == AffordabilityCategory.EXPENSIVE:
                conditions.append(
                    and_(
                        TuitionData.tuition_in_state >= 40000,
                        TuitionData.tuition_in_state < 55000,
                    )
                )
            else:  # VERY_EXPENSIVE
                conditions.append(TuitionData.tuition_in_state >= 55000)

        if filters.has_comprehensive_data is not None:
            if filters.has_comprehensive_data:
                conditions.append(
                    and_(
                        TuitionData.has_tuition_data == True,
                        TuitionData.has_fees_data == True,
                        TuitionData.has_living_data == True,
                    )
                )

        if filters.validation_status is not None:
            conditions.append(
                TuitionData.validation_status == filters.validation_status
            )

        if filters.state is not None:
            conditions.append(Institution.state == filters.state)

        if conditions:
            query = query.filter(and_(*conditions))

        # Get total count
        total_count = query.count()

        # Apply pagination and ordering
        results = (
            query.order_by(desc(TuitionData.data_completeness_score))
            .offset(offset)
            .limit(limit)
            .all()
        )

        return results, total_count

    def get_affordability_analysis(
        self, request: AffordabilityRequest
    ) -> Dict[str, Any]:
        """Analyze affordability for a given income and residency status"""
        query = self.db.query(TuitionData).filter(TuitionData.has_tuition_data == True)

        # Choose the appropriate tuition field based on residency
        if request.residency_status == "in_state":
            tuition_field = TuitionData.tuition_fees_in_state
        else:
            tuition_field = TuitionData.tuition_fees_out_state

        # Calculate affordability thresholds based on income
        # Rule of thumb: total education costs shouldn't exceed 10-15% of gross income
        max_affordable_annual = request.family_income * 0.125  # 12.5%

        affordable_count = query.filter(tuition_field <= max_affordable_annual).count()
        total_count = query.count()

        # Get distribution by price ranges
        price_ranges = [
            ("under_10k", tuition_field < 10000),
            ("10k_to_25k", and_(tuition_field >= 10000, tuition_field < 25000)),
            ("25k_to_40k", and_(tuition_field >= 25000, tuition_field < 40000)),
            ("40k_to_55k", and_(tuition_field >= 40000, tuition_field < 55000)),
            ("over_55k", tuition_field >= 55000),
        ]

        distribution = {}
        for range_name, condition in price_ranges:
            count = query.filter(condition).count()
            distribution[range_name] = {
                "count": count,
                "percentage": (
                    round((count / total_count) * 100, 1) if total_count > 0 else 0
                ),
            }

        return {
            "total_institutions": total_count,
            "affordable_institutions": affordable_count,
            "affordability_rate": (
                round((affordable_count / total_count) * 100, 1)
                if total_count > 0
                else 0
            ),
            "max_affordable_annual_cost": round(max_affordable_annual, 2),
            "residency_status": request.residency_status,
            "family_income": request.family_income,
            "price_distribution": distribution,
            "recommendation": self._get_affordability_recommendation(
                request, affordable_count, total_count
            ),
        }

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        total_records = self.db.query(TuitionData).count()

        if total_records == 0:
            return {"error": "No tuition data available"}

        # Basic statistics
        stats = {}

        # In-state tuition statistics
        in_state_query = self.db.query(TuitionData.tuition_in_state).filter(
            TuitionData.tuition_in_state.isnot(None)
        )
        in_state_values = [row[0] for row in in_state_query.all()]

        if in_state_values:
            stats["in_state_tuition"] = {
                "count": len(in_state_values),
                "mean": round(np.mean(in_state_values), 2),
                "median": round(np.median(in_state_values), 2),
                "min": round(min(in_state_values), 2),
                "max": round(max(in_state_values), 2),
                "p25": round(np.percentile(in_state_values, 25), 2),
                "p75": round(np.percentile(in_state_values, 75), 2),
            }

        # Out-of-state tuition statistics
        out_state_query = self.db.query(TuitionData.tuition_out_state).filter(
            TuitionData.tuition_out_state.isnot(None)
        )
        out_state_values = [row[0] for row in out_state_query.all()]

        if out_state_values:
            stats["out_state_tuition"] = {
                "count": len(out_state_values),
                "mean": round(np.mean(out_state_values), 2),
                "median": round(np.median(out_state_values), 2),
                "min": round(min(out_state_values), 2),
                "max": round(max(out_state_values), 2),
                "p25": round(np.percentile(out_state_values, 25), 2),
                "p75": round(np.percentile(out_state_values, 75), 2),
            }

        # Data quality metrics
        data_quality = {
            "total_records": total_records,
            "with_tuition_data": self.db.query(TuitionData)
            .filter(TuitionData.has_tuition_data == True)
            .count(),
            "with_fees_data": self.db.query(TuitionData)
            .filter(TuitionData.has_fees_data == True)
            .count(),
            "with_living_data": self.db.query(TuitionData)
            .filter(TuitionData.has_living_data == True)
            .count(),
            "comprehensive_data": self.db.query(TuitionData)
            .filter(
                and_(
                    TuitionData.has_tuition_data == True,
                    TuitionData.has_fees_data == True,
                    TuitionData.has_living_data == True,
                )
            )
            .count(),
        }

        # Validation status distribution
        validation_stats = {}
        for status in ValidationStatus:
            count = (
                self.db.query(TuitionData)
                .filter(TuitionData.validation_status == status)
                .count()
            )
            validation_stats[status.value] = count

        return {
            "dataset_info": {
                "total_institutions": total_records,
                "last_updated": datetime.utcnow().isoformat(),
                "academic_year": "2023-24",
            },
            "tuition_statistics": stats,
            "data_quality_metrics": data_quality,
            "validation_status_distribution": validation_stats,
            "affordability_distribution": self._calculate_affordability_distribution(),
        }

    # Private helper methods
    def _update_data_quality_indicators(self, tuition_data: TuitionData) -> None:
        """Update data quality indicators for a tuition record"""
        # Check if has tuition data
        tuition_data.has_tuition_data = (
            tuition_data.tuition_in_state is not None
            or tuition_data.tuition_out_state is not None
        )

        # Check if has fees data
        tuition_data.has_fees_data = (
            tuition_data.required_fees_in_state is not None
            or tuition_data.required_fees_out_state is not None
        )

        # Check if has living data
        tuition_data.has_living_data = (
            tuition_data.room_board_on_campus is not None
            or tuition_data.room_board_off_campus is not None
            or tuition_data.books_supplies is not None
        )

        # Calculate completeness score (0-100)
        score = 0
        total_fields = 0

        # Core tuition fields (40% weight)
        tuition_fields = [
            tuition_data.tuition_in_state,
            tuition_data.tuition_out_state,
            tuition_data.tuition_fees_in_state,
            tuition_data.tuition_fees_out_state,
        ]
        for field in tuition_fields:
            total_fields += 10
            if field is not None and field > 0:
                score += 10

        # Living expense fields (35% weight)
        living_fields = [
            tuition_data.room_board_on_campus,
            tuition_data.room_board_off_campus,
            tuition_data.books_supplies,
            tuition_data.personal_expenses,
            tuition_data.transportation,
        ]
        for field in living_fields:
            total_fields += 7
            if field is not None and field > 0:
                score += 7

        # Fee fields (25% weight)
        fee_fields = [
            tuition_data.required_fees_in_state,
            tuition_data.required_fees_out_state,
        ]
        for field in fee_fields:
            total_fields += 12
            if field is not None and field > 0:
                score += 12

        tuition_data.data_completeness_score = (
            min(100, score) if total_fields > 0 else 0
        )

        # Set validation status based on data quality
        if tuition_data.data_completeness_score >= 80:
            tuition_data.validation_status = ValidationStatus.VALIDATED
        elif tuition_data.data_completeness_score >= 50:
            tuition_data.validation_status = ValidationStatus.NEEDS_REVIEW
        else:
            tuition_data.validation_status = ValidationStatus.PENDING

    def _calculate_affordability_distribution(self) -> Dict[AffordabilityCategory, int]:
        """Calculate distribution of institutions by affordability category"""
        distribution = {}

        for category in AffordabilityCategory:
            if category == AffordabilityCategory.VERY_AFFORDABLE:
                count = (
                    self.db.query(TuitionData)
                    .filter(TuitionData.tuition_in_state < 10000)
                    .count()
                )
            elif category == AffordabilityCategory.AFFORDABLE:
                count = (
                    self.db.query(TuitionData)
                    .filter(
                        and_(
                            TuitionData.tuition_in_state >= 10000,
                            TuitionData.tuition_in_state < 25000,
                        )
                    )
                    .count()
                )
            elif category == AffordabilityCategory.MODERATE:
                count = (
                    self.db.query(TuitionData)
                    .filter(
                        and_(
                            TuitionData.tuition_in_state >= 25000,
                            TuitionData.tuition_in_state < 40000,
                        )
                    )
                    .count()
                )
            elif category == AffordabilityCategory.EXPENSIVE:
                count = (
                    self.db.query(TuitionData)
                    .filter(
                        and_(
                            TuitionData.tuition_in_state >= 40000,
                            TuitionData.tuition_in_state < 55000,
                        )
                    )
                    .count()
                )
            else:  # VERY_EXPENSIVE
                count = (
                    self.db.query(TuitionData)
                    .filter(TuitionData.tuition_in_state >= 55000)
                    .count()
                )

            distribution[category] = count

        return distribution

    def _get_affordability_recommendation(
        self, request: AffordabilityRequest, affordable_count: int, total_count: int
    ) -> str:
        """Generate affordability recommendation"""
        affordability_rate = (
            (affordable_count / total_count) * 100 if total_count > 0 else 0
        )

        if affordability_rate >= 75:
            return "Excellent! You have many affordable options to choose from."
        elif affordability_rate >= 50:
            return "Good news! You have a solid selection of affordable institutions."
        elif affordability_rate >= 25:
            return "Consider expanding your search criteria or exploring financial aid options."
        else:
            return "Limited affordable options. Strongly recommend exploring financial aid, scholarships, and community college transfer programs."
