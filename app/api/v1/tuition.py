# app/api/v1/tuition.py
"""
FastAPI endpoints for tuition data and projections
Updated to match new TuitionData model and schema structure
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import numpy as np

from app.core.database import get_db
from app.models.tuition import TuitionData
from app.models.institution import Institution
from app.schemas.tuition import (
    TuitionDataResponse,
    TuitionProjectionResponse,
    TuitionAnalyticsResponse,
    AffordabilityRequest,
    AffordabilityAnalysis,
    ProjectionRequest,
    TuitionSearchFilters,
    TuitionSearchResponse,
    InstitutionWithTuitionData,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class TuitionProjectionCalculator:
    """Calculate tuition projections based on historical trends"""

    def __init__(self):
        # Education inflation rates (higher than general CPI)
        self.inflation_rates = {
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
                    rate = self.inflation_rates.get(year, 0.035)
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
                or self.inflation_rates.get(target_year, 0.035),
                "confidence_level": (
                    "high"
                    if target_year <= 2025
                    else "medium" if target_year <= 2027 else "low"
                ),
            }

            projections.append(projection)

        return projections


# API Endpoints
@router.get("/institution/{ipeds_id}", response_model=TuitionDataResponse)
async def get_tuition_by_institution(ipeds_id: int, db: Session = Depends(get_db)):
    """Get tuition data for a specific institution"""
    try:
        # Query tuition data with institution info
        result = (
            db.query(TuitionData, Institution)
            .join(Institution, TuitionData.ipeds_id == Institution.ipeds_id)
            .filter(TuitionData.ipeds_id == ipeds_id)
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        tuition_data, institution = result

        # Convert to response using the model's to_dict method
        response_data = tuition_data.to_dict()
        response_data["institution_name"] = institution.name

        return TuitionDataResponse(**response_data)

    except Exception as e:
        logger.error(f"Error fetching tuition data for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/institution/{ipeds_id}/projections")
async def get_tuition_projections(
    ipeds_id: int,
    request: ProjectionRequest = Depends(),
    db: Session = Depends(get_db),
):
    """Get tuition projections for a specific institution"""
    try:
        tuition_data = (
            db.query(TuitionData).filter(TuitionData.ipeds_id == ipeds_id).first()
        )

        if not tuition_data:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        calculator = TuitionProjectionCalculator()
        projections = calculator.calculate_projections(
            tuition_data=tuition_data,
            years=request.years,
            custom_inflation_rate=request.inflation_rate,
        )

        return {
            "ipeds_id": ipeds_id,
            "projections": projections,
            "projection_methodology": "Education inflation rates applied to base year data",
            "base_year": "2023-24",
            "custom_inflation_rate": request.inflation_rate,
        }

    except Exception as e:
        logger.error(f"Error generating projections for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics", response_model=TuitionAnalyticsResponse)
async def get_tuition_analytics(db: Session = Depends(get_db)):
    """Get comprehensive tuition analytics"""
    try:
        # Get all tuition data for analytics
        all_data = (
            db.query(TuitionData).filter(TuitionData.has_tuition_data == True).all()
        )

        if not all_data:
            raise HTTPException(status_code=404, detail="No tuition data available")

        # Calculate statistics
        in_state_tuitions = [d.tuition_in_state for d in all_data if d.tuition_in_state]
        out_state_tuitions = [
            d.tuition_out_state for d in all_data if d.tuition_out_state
        ]
        room_board_costs = [
            d.room_board_on_campus for d in all_data if d.room_board_on_campus
        ]

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

        analytics = {
            "dataset_info": {
                "total_institutions": len(all_data),
                "academic_year": "2023-24",
                "last_updated": datetime.now().isoformat(),
            },
            "tuition_statistics": {
                "in_state_tuition": calculate_stats(in_state_tuitions),
                "out_of_state_tuition": calculate_stats(out_state_tuitions),
                "room_and_board": calculate_stats(room_board_costs),
            },
            "affordability_distribution": affordability_distribution,
            "data_quality_metrics": {
                "institutions_with_comprehensive_data": sum(
                    1 for d in all_data if d.has_comprehensive_data
                ),
                "average_completeness_score": round(
                    np.mean([d.data_completeness_score for d in all_data]), 1
                ),
            },
        }

        return TuitionAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/affordability/analyze")
async def analyze_affordability(
    ipeds_id: int,
    request: AffordabilityRequest,
    db: Session = Depends(get_db),
):
    """Analyze affordability for a specific institution and household income"""
    try:
        tuition_data = (
            db.query(TuitionData).filter(TuitionData.ipeds_id == ipeds_id).first()
        )

        if not tuition_data:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        analysis = tuition_data.analyze_affordability(
            household_income=request.household_income,
            residency=request.residency_status,
        )

        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])

        return AffordabilityAnalysis(**analysis)

    except Exception as e:
        logger.error(f"Error analyzing affordability: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search")
async def search_institutions(
    min_tuition_in_state: Optional[float] = Query(None, ge=0),
    max_tuition_in_state: Optional[float] = Query(None, ge=0),
    min_tuition_out_state: Optional[float] = Query(None, ge=0),
    max_tuition_out_state: Optional[float] = Query(None, ge=0),
    affordability_category: Optional[str] = Query(None),
    state: Optional[str] = Query(None, max_length=2),
    has_comprehensive_data: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search institutions by tuition criteria"""
    try:
        # Build query
        query = (
            db.query(TuitionData, Institution)
            .join(Institution, TuitionData.ipeds_id == Institution.ipeds_id)
            .filter(TuitionData.has_tuition_data == True)
        )

        # Apply filters
        if min_tuition_in_state is not None:
            query = query.filter(TuitionData.tuition_in_state >= min_tuition_in_state)
        if max_tuition_in_state is not None:
            query = query.filter(TuitionData.tuition_in_state <= max_tuition_in_state)
        if min_tuition_out_state is not None:
            query = query.filter(TuitionData.tuition_out_state >= min_tuition_out_state)
        if max_tuition_out_state is not None:
            query = query.filter(TuitionData.tuition_out_state <= max_tuition_out_state)
        if state:
            query = query.filter(Institution.state == state.upper())
        if has_comprehensive_data is not None:
            if has_comprehensive_data:
                query = query.filter(
                    TuitionData.tuition_in_state.isnot(None),
                    TuitionData.tuition_out_state.isnot(None),
                    TuitionData.room_board_on_campus.isnot(None),
                )

        # Count total results
        total_count = query.count()

        # Apply pagination and get results
        results = query.offset(offset).limit(limit).all()

        # Format results
        institutions = []
        for tuition_data, institution in results:
            institution_data = {
                "ipeds_id": institution.ipeds_id,
                "name": institution.name,
                "city": institution.city,
                "state": institution.state,
                "control_type": (
                    institution.control_type.value if institution.control_type else None
                ),
                "size_category": (
                    institution.size_category.value
                    if institution.size_category
                    else None
                ),
                "tuition_data": TuitionDataResponse(**tuition_data.to_dict()),
                "has_tuition_data": tuition_data.has_tuition_data,
                "tuition_summary": (
                    f"In-state: ${tuition_data.tuition_in_state:,.0f}"
                    if tuition_data.tuition_in_state
                    else "Data not available"
                ),
            }
            institutions.append(InstitutionWithTuitionData(**institution_data))

        return TuitionSearchResponse(
            filters=TuitionSearchFilters(
                min_tuition_in_state=min_tuition_in_state,
                max_tuition_in_state=max_tuition_in_state,
                min_tuition_out_state=min_tuition_out_state,
                max_tuition_out_state=max_tuition_out_state,
                affordability_category=affordability_category,
                state=state,
                has_comprehensive_data=has_comprehensive_data,
            ),
            total_count=total_count,
            results=institutions,
        )

    except Exception as e:
        logger.error(f"Error searching institutions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/institution/{ipeds_id}/full")
async def get_institution_with_tuition(ipeds_id: int, db: Session = Depends(get_db)):
    """Get complete institution information with tuition data for frontend display"""
    try:
        # Query institution with tuition data
        result = (
            db.query(Institution, TuitionData)
            .outerjoin(TuitionData, Institution.ipeds_id == TuitionData.ipeds_id)
            .filter(Institution.ipeds_id == ipeds_id)
            .first()
        )

        if not result:
            raise HTTPException(status_code=404, detail="Institution not found")

        institution, tuition_data = result

        # Build response
        response = {
            "ipeds_id": institution.ipeds_id,
            "name": institution.name,
            "city": institution.city,
            "state": institution.state,
            "control_type": (
                institution.control_type.value if institution.control_type else None
            ),
            "size_category": (
                institution.size_category.value if institution.size_category else None
            ),
            "website": getattr(institution, "website", None),
            "has_tuition_data": tuition_data is not None,
        }

        if tuition_data:
            response["tuition_data"] = TuitionDataResponse(**tuition_data.to_dict())
            response["tuition_summary"] = (
                f"In-state: ${tuition_data.tuition_in_state:,.0f}, Out-of-state: ${tuition_data.tuition_out_state:,.0f}"
            )
        else:
            response["tuition_data"] = None
            response["tuition_summary"] = "Tuition data not available"

        return InstitutionWithTuitionData(**response)

    except Exception as e:
        logger.error(
            f"Error fetching institution with tuition data for {ipeds_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
