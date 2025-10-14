# app/api/v1/tuition.py
"""
Refactored FastAPI endpoints for tuition data using service layer
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.core.database import get_db
from app.services.tuition import TuitionService
from app.schemas.tuition import (
    TuitionDataResponse,
    TuitionDataCreate,
    TuitionDataUpdate,
    TuitionProjectionResponse,
    TuitionAnalyticsResponse,
    AffordabilityRequest,
    AffordabilityAnalysis,
    ProjectionRequest,
    TuitionSearchFilters,
    TuitionSearchResponse,
    InstitutionWithTuitionData,
    AffordabilityCategory,
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
        tuition_data,
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
                "projected_total_cost_in_state": round(
                    (base_tuition_in + base_room_board) * cumulative_rate,
                    2,
                ),
                "projected_total_cost_out_state": round(
                    (base_tuition_out + base_room_board) * cumulative_rate,
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
        tuition_service = TuitionService(db)
        tuition_data = tuition_service.get_by_ipeds_id(ipeds_id)

        if not tuition_data:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        return TuitionDataResponse(**tuition_data.to_dict())

    except Exception as e:
        logger.error(f"Error fetching tuition data for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=TuitionDataResponse)
async def create_tuition_data(
    tuition_data: TuitionDataCreate, db: Session = Depends(get_db)
):
    """Create new tuition data record"""
    try:
        tuition_service = TuitionService(db)

        # Check if data already exists for this institution
        existing = tuition_service.get_by_ipeds_id(tuition_data.ipeds_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Tuition data already exists for institution {tuition_data.ipeds_id}",
            )

        created_tuition = tuition_service.create(tuition_data)
        return TuitionDataResponse(**created_tuition.to_dict())

    except Exception as e:
        logger.error(f"Error creating tuition data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/institution/{ipeds_id}", response_model=TuitionDataResponse)
async def update_tuition_data(
    ipeds_id: int, update_data: TuitionDataUpdate, db: Session = Depends(get_db)
):
    """Update tuition data for an institution"""
    try:
        tuition_service = TuitionService(db)
        updated_tuition = tuition_service.update(ipeds_id, update_data)

        if not updated_tuition:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        return TuitionDataResponse(**updated_tuition.to_dict())

    except Exception as e:
        logger.error(f"Error updating tuition data for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/institution/{ipeds_id}")
async def delete_tuition_data(ipeds_id: int, db: Session = Depends(get_db)):
    """Delete tuition data for an institution"""
    try:
        tuition_service = TuitionService(db)
        deleted = tuition_service.delete(ipeds_id)

        if not deleted:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        return {"message": f"Tuition data deleted for institution {ipeds_id}"}

    except Exception as e:
        logger.error(f"Error deleting tuition data for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/institution/{ipeds_id}/projections")
async def get_tuition_projections(
    ipeds_id: int,
    years: int = Query(5, ge=1, le=10, description="Number of years to project"),
    inflation_rate: Optional[float] = Query(
        None, ge=0.0, le=0.15, description="Custom inflation rate"
    ),
    db: Session = Depends(get_db),
):
    """Get tuition projections for a specific institution"""
    try:
        tuition_service = TuitionService(db)
        tuition_data = tuition_service.get_by_ipeds_id(ipeds_id)

        if not tuition_data:
            raise HTTPException(
                status_code=404, detail="Institution tuition data not found"
            )

        calculator = TuitionProjectionCalculator()
        projections = calculator.calculate_projections(
            tuition_data=tuition_data,
            years=years,
            custom_inflation_rate=inflation_rate,
        )

        return {
            "ipeds_id": ipeds_id,
            "projections": projections,
            "projection_methodology": "Education inflation rates applied to base year data",
            "base_year": "2023-24",
            "custom_inflation_rate": inflation_rate,
        }

    except Exception as e:
        logger.error(f"Error generating projections for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=TuitionSearchResponse)
async def search_institutions(
    # Tuition filters
    min_tuition_in_state: Optional[float] = Query(None, ge=0),
    max_tuition_in_state: Optional[float] = Query(None, ge=0),
    min_tuition_out_state: Optional[float] = Query(None, ge=0),
    max_tuition_out_state: Optional[float] = Query(None, ge=0),
    min_total_cost: Optional[float] = Query(None, ge=0),
    max_total_cost: Optional[float] = Query(None, ge=0),
    affordability_category: Optional[AffordabilityCategory] = Query(None),
    has_comprehensive_data: Optional[bool] = Query(None),
    state: Optional[str] = Query(None, max_length=2),
    # Pagination
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search institutions with tuition data"""
    try:
        # Build filters
        filters = TuitionSearchFilters(
            min_tuition_in_state=min_tuition_in_state,
            max_tuition_in_state=max_tuition_in_state,
            min_tuition_out_state=min_tuition_out_state,
            max_tuition_out_state=max_tuition_out_state,
            min_total_cost=min_total_cost,
            max_total_cost=max_total_cost,
            affordability_category=affordability_category,
            has_comprehensive_data=has_comprehensive_data,
            state=state,
        )

        tuition_service = TuitionService(db)
        results, total_count = tuition_service.search_institutions(
            filters=filters, limit=limit, offset=offset
        )

        # Convert results to response format
        tuition_responses = []
        for tuition_data in results:
            tuition_responses.append(TuitionDataResponse(**tuition_data.to_dict()))

        return TuitionSearchResponse(
            filters=filters,
            total_count=total_count,
            results=tuition_responses,
        )

    except Exception as e:
        logger.error(f"Error searching institutions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/affordability-analysis", response_model=AffordabilityAnalysis)
async def analyze_affordability(
    request: AffordabilityRequest, db: Session = Depends(get_db)
):
    """Analyze affordability for a given income and residency status"""
    try:
        tuition_service = TuitionService(db)
        analysis = tuition_service.get_affordability_analysis(request)

        return AffordabilityAnalysis(**analysis)

    except Exception as e:
        logger.error(f"Error analyzing affordability: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics", response_model=TuitionAnalyticsResponse)
async def get_tuition_analytics(db: Session = Depends(get_db)):
    """Get comprehensive tuition analytics"""
    try:
        tuition_service = TuitionService(db)
        analytics = tuition_service.get_analytics_summary()

        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])

        return TuitionAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"Error getting tuition analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bulk-create")
async def bulk_create_tuition_data(
    tuition_records: List[TuitionDataCreate], db: Session = Depends(get_db)
):
    """Bulk create tuition data records - useful for data imports"""
    try:
        if len(tuition_records) > 1000:
            raise HTTPException(
                status_code=400, detail="Maximum 1000 records per bulk operation"
            )

        tuition_service = TuitionService(db)
        created_count = tuition_service.bulk_create(tuition_records)

        return {
            "message": f"Successfully created {created_count} tuition records",
            "created_count": created_count,
        }

    except Exception as e:
        logger.error(f"Error bulk creating tuition data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary")
async def get_tuition_stats_summary(db: Session = Depends(get_db)):
    """Get quick tuition statistics summary"""
    try:
        tuition_service = TuitionService(db)
        analytics = tuition_service.get_analytics_summary()

        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])

        # Return simplified stats for dashboard use
        return {
            "total_institutions": analytics["dataset_info"]["total_institutions"],
            "data_quality": analytics["data_quality_metrics"],
            "tuition_ranges": {
                "in_state": analytics["tuition_statistics"].get("in_state_tuition", {}),
                "out_state": analytics["tuition_statistics"].get(
                    "out_state_tuition", {}
                ),
            },
            "affordability_distribution": analytics["affordability_distribution"],
        }

    except Exception as e:
        logger.error(f"Error getting tuition stats summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Integration endpoint for frontend institution pages
@router.get("/institution/{ipeds_id}/full")
async def get_institution_with_tuition(ipeds_id: int, db: Session = Depends(get_db)):
    """Get complete institution information with tuition data for frontend display"""
    try:
        from app.models.institution import Institution

        # Query institution with tuition data using service
        tuition_service = TuitionService(db)
        tuition_data = tuition_service.get_by_ipeds_id(ipeds_id)

        # Get institution data
        institution = (
            db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
        )

        if not institution:
            raise HTTPException(status_code=404, detail="Institution not found")

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
            if tuition_data.tuition_in_state and tuition_data.tuition_out_state:
                response["tuition_summary"] = (
                    f"In-state: ${tuition_data.tuition_in_state:,.0f}, "
                    f"Out-of-state: ${tuition_data.tuition_out_state:,.0f}"
                )
            else:
                response["tuition_summary"] = "Partial tuition data available"
        else:
            response["tuition_data"] = None
            response["tuition_summary"] = "Tuition data not available"

        return response

    except Exception as e:
        logger.error(
            f"Error fetching institution with tuition data for {ipeds_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
