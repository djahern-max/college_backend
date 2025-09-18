# app/services/tuition.py
"""
Tuition Service - Business logic for tuition projections and analysis
Integrates with your existing MagicScholar service architecture
"""

from sqlalchemy.orm import Session, joinedload
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

    # Business Logic Methods
    def get_with_institution_data(
        self, ipeds_id: int
    ) -> Optional[Tuple[TuitionData, Institution]]:
        """Get tuition data with associated institution information"""
        result = (
            self.db.query(TuitionData, Institution)
            .join(Institution, TuitionData.ipeds_id == Institution.ipeds_id)
            .filter(TuitionData.ipeds_id == ipeds_id)
            .first()
        )
        return result

    def search_institutions(
        self, filters: TuitionSearchFilters, page: int = 1, per_page: int = 50
    ) -> Tuple[List[Tuple[TuitionData, Institution]], int]:
        """Search institutions with tuition filters"""

        # Base query with institution join
        query = (
            self.db.query(TuitionData, Institution)
            .join(Institution, TuitionData.ipeds_id == Institution.ipeds_id)
            .filter(TuitionData.has_tuition_data == True)
        )

        # Apply filters
        if filters.min_tuition_in_state is not None:
            query = query.filter(
                TuitionData.tuition_in_state >= filters.min_tuition_in_state
            )

        if filters.max_tuition_in_state is not None:
            query = query.filter(
                TuitionData.tuition_in_state <= filters.max_tuition_in_state
            )

        if filters.min_tuition_out_state is not None:
            query = query.filter(
                TuitionData.tuition_out_state >= filters.min_tuition_out_state
            )

        if filters.max_tuition_out_state is not None:
            query = query.filter(
                TuitionData.tuition_out_state <= filters.max_tuition_out_state
            )

        if filters.affordability_category:
            # This is a calculated field, so we need to filter in memory or use a subquery
            # For now, we'll apply this filter after the query
            pass

        if filters.state:
            query = query.filter(Institution.state == filters.state.upper())

        if filters.has_comprehensive_data is not None:
            if filters.has_comprehensive_data:
                query = query.filter(
                    TuitionData.tuition_in_state.isnot(None),
                    TuitionData.tuition_out_state.isnot(None),
                    TuitionData.room_board_on_campus.isnot(None),
                )

        if filters.validation_status:
            query = query.filter(
                TuitionData.validation_status == filters.validation_status
            )

        # Count total results
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()

        # Apply affordability category filter in memory if needed
        if filters.affordability_category:
            filtered_results = []
            for tuition_data, institution in results:
                if (
                    tuition_data.affordability_category
                    == filters.affordability_category.value
                ):
                    filtered_results.append((tuition_data, institution))
            results = filtered_results

        return results, total_count

    def calculate_projections(
        self, ipeds_id: int, request: ProjectionRequest
    ) -> Optional[Dict[str, Any]]:
        """Calculate tuition projections for an institution"""

        tuition_data = self.get_by_ipeds_id(ipeds_id)
        if not tuition_data:
            return None

        calculator = TuitionProjectionCalculator()
        projections = calculator.calculate_projections(
            tuition_data=tuition_data,
            years=request.years,
            custom_inflation_rate=request.inflation_rate,
        )

        return {
            "ipeds_id": ipeds_id,
            "base_year": "2023-24",
            "projections": projections,
            "methodology": "Education inflation rates applied to base year data",
            "custom_inflation_rate": request.inflation_rate,
        }

    def analyze_affordability(
        self, ipeds_id: int, request: AffordabilityRequest
    ) -> Optional[Dict[str, Any]]:
        """Analyze affordability for an institution and household income"""

        tuition_data = self.get_by_ipeds_id(ipeds_id)
        if not tuition_data:
            return None

        return tuition_data.analyze_affordability(
            household_income=request.household_income,
            residency=request.residency_status,
        )

    def get_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive tuition analytics"""

        # Get all institutions with tuition data
        all_data = (
            self.db.query(TuitionData)
            .filter(TuitionData.has_tuition_data == True)
            .all()
        )

        if not all_data:
            return {}

        # Extract values for statistics
        in_state_tuitions = [d.tuition_in_state for d in all_data if d.tuition_in_state]
        out_state_tuitions = [
            d.tuition_out_state for d in all_data if d.tuition_out_state
        ]
        room_board_costs = [
            d.room_board_on_campus for d in all_data if d.room_board_on_campus
        ]
        books_costs = [d.books_supplies for d in all_data if d.books_supplies]

        # Calculate statistics
        def calculate_stats(values):
            if not values:
                return None
            return {
                "count": len(values),
                "mean": round(np.mean(values), 2),
                "median": round(np.median(values), 2),
                "p25": round(np.percentile(values, 25), 2),
                "p75": round(np.percentile(values, 75), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
            }

        # Create affordability distribution
        affordability_distribution = {}
        for data in all_data:
            category = data.affordability_category
            affordability_distribution[category] = (
                affordability_distribution.get(category, 0) + 1
            )

        # Data quality metrics
        institutions_with_comprehensive_data = sum(
            1 for d in all_data if d.has_comprehensive_data
        )

        average_completeness_score = round(
            np.mean([d.data_completeness_score for d in all_data]), 1
        )

        return {
            "dataset_info": {
                "total_institutions": len(all_data),
                "academic_year": "2023-24",
                "last_updated": datetime.now().isoformat(),
                "data_source": "IPEDS IC2023_AY",
            },
            "tuition_statistics": {
                "in_state_tuition": calculate_stats(in_state_tuitions),
                "out_of_state_tuition": calculate_stats(out_state_tuitions),
                "room_and_board": calculate_stats(room_board_costs),
                "books_and_supplies": calculate_stats(books_costs),
            },
            "affordability_distribution": affordability_distribution,
            "data_quality_metrics": {
                "institutions_with_comprehensive_data": institutions_with_comprehensive_data,
                "comprehensive_data_rate": round(
                    (institutions_with_comprehensive_data / len(all_data)) * 100, 1
                ),
                "average_completeness_score": average_completeness_score,
            },
        }

    def get_institutions_by_affordability(
        self, category: str, limit: int = 50
    ) -> List[Tuple[TuitionData, Institution]]:
        """Get institutions filtered by affordability category"""

        # Get all institutions with tuition data
        results = (
            self.db.query(TuitionData, Institution)
            .join(Institution, TuitionData.ipeds_id == Institution.ipeds_id)
            .filter(TuitionData.has_tuition_data == True)
            .limit(limit * 2)  # Get more than needed since we'll filter in memory
            .all()
        )

        # Filter by affordability category in memory
        filtered_results = []
        for tuition_data, institution in results:
            if tuition_data.affordability_category == category:
                filtered_results.append((tuition_data, institution))
                if len(filtered_results) >= limit:
                    break

        return filtered_results

    def bulk_import(self, tuition_records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Bulk import tuition data records"""

        created_count = 0
        updated_count = 0
        error_count = 0

        for record in tuition_records:
            try:
                ipeds_id = record.get("ipeds_id")
                if not ipeds_id:
                    error_count += 1
                    continue

                # Check if record exists
                existing = self.get_by_ipeds_id(ipeds_id)

                if existing:
                    # Update existing record
                    for field, value in record.items():
                        if hasattr(existing, field) and field != "id":
                            setattr(existing, field, value)

                    self._update_data_quality_indicators(existing)
                    updated_count += 1
                else:
                    # Create new record
                    new_record = TuitionData(**record)
                    self._update_data_quality_indicators(new_record)
                    self.db.add(new_record)
                    created_count += 1

            except Exception as e:
                logger.error(
                    f"Error processing record for IPEDS {record.get('ipeds_id')}: {e}"
                )
                error_count += 1

        # Commit all changes
        try:
            self.db.commit()
            logger.info(
                f"Bulk import completed: {created_count} created, {updated_count} updated, {error_count} errors"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Bulk import failed: {e}")
            raise

        return {
            "created": created_count,
            "updated": updated_count,
            "errors": error_count,
            "total": len(tuition_records),
        }

    # Private Helper Methods
    def _update_data_quality_indicators(self, tuition_data: TuitionData):
        """Update data quality indicators for a tuition record"""

        # Check what data is available
        tuition_data.has_tuition_data = bool(
            tuition_data.tuition_in_state or tuition_data.tuition_out_state
        )

        tuition_data.has_fees_data = bool(
            tuition_data.required_fees_in_state or tuition_data.required_fees_out_state
        )

        tuition_data.has_living_data = bool(
            tuition_data.room_board_on_campus
            or tuition_data.books_supplies
            or tuition_data.personal_expenses
        )

        # Calculate completeness score
        score = 0
        if tuition_data.tuition_in_state:
            score += 25
        if tuition_data.tuition_out_state:
            score += 25
        if tuition_data.room_board_on_campus:
            score += 15
        if tuition_data.books_supplies:
            score += 10
        if tuition_data.personal_expenses:
            score += 10
        if tuition_data.required_fees_in_state or tuition_data.required_fees_out_state:
            score += 15

        tuition_data.data_completeness_score = score

        # Update validation status
        if score >= 85:
            tuition_data.validation_status = "clean"
        elif score >= 50:
            tuition_data.validation_status = "incomplete"
        elif score > 0:
            tuition_data.validation_status = "pending"
        else:
            tuition_data.validation_status = "error"


class TuitionProjectionCalculator:
    """Calculate tuition projections based on historical trends"""

    def __init__(self):
        # Education inflation rates (higher than general CPI)
        self.default_inflation_rates = {
            2024: 0.045,  # 4.5%
            2025: 0.042,  # 4.2%
            2026: 0.040,  # 4.0%
            2027: 0.038,  # 3.8%
            2028: 0.035,  # 3.5%
            2029: 0.035,  # 3.5% (default)
            2030: 0.035,  # 3.5% (default)
        }

    def calculate_projections(
        self,
        tuition_data: TuitionData,
        years: int = 5,
        custom_inflation_rate: Optional[float] = None,
        base_year: int = 2023,
    ) -> List[Dict[str, Any]]:
        """Calculate projections for multiple years"""

        projections = []

        # Base values from the tuition data
        base_tuition_in = tuition_data.tuition_in_state or 0
        base_tuition_out = tuition_data.tuition_out_state or base_tuition_in * 1.5
        base_room_board = tuition_data.room_board_on_campus or 12000
        base_books = tuition_data.books_supplies or 1200
        base_personal = tuition_data.personal_expenses or 3000

        for target_year in range(base_year + 1, base_year + years + 1):
            if custom_inflation_rate is not None:
                # Use custom rate
                rate = custom_inflation_rate
                cumulative_rate = (1 + rate) ** (target_year - base_year)
            else:
                # Use graduated rates
                cumulative_rate = 1.0
                for year in range(base_year + 1, target_year + 1):
                    rate = self.default_inflation_rates.get(year, 0.035)
                    cumulative_rate *= 1 + rate

            projection = {
                "academic_year": f"{target_year}-{str(target_year+1)[2:]}",
                "projected_in_state_tuition": round(
                    base_tuition_in * cumulative_rate, 2
                ),
                "projected_out_state_tuition": round(
                    base_tuition_out * cumulative_rate, 2
                ),
                "projected_room_board": round(base_room_board * cumulative_rate, 2),
                "projected_books_supplies": round(base_books * cumulative_rate, 2),
                "projected_personal_expenses": round(
                    base_personal * cumulative_rate, 2
                ),
                "projected_total_cost_in_state": round(
                    (base_tuition_in + base_room_board + base_books + base_personal)
                    * cumulative_rate,
                    2,
                ),
                "projected_total_cost_out_state": round(
                    (base_tuition_out + base_room_board + base_books + base_personal)
                    * cumulative_rate,
                    2,
                ),
                "inflation_rate_used": custom_inflation_rate
                or self.default_inflation_rates.get(target_year, 0.035),
                "confidence_level": (
                    "high"
                    if target_year <= 2025
                    else "medium" if target_year <= 2027 else "low"
                ),
            }

            projections.append(projection)

        return projections
