# app/api/v1/costs.py
"""
Simple costs API for retrieving tuition and cost data for institutions.
Focuses on frontend display needs.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.tuition import TuitionData
from app.models.institution import Institution

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/institution/{ipeds_id}")
async def get_institution_costs(ipeds_id: int, db: Session = Depends(get_db)):
    """
    Get cost data for a specific institution by IPEDS ID.
    Returns the most recent tuition data available.
    """
    try:
        # Get institution to verify it exists
        institution = (
            db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
        )

        if not institution:
            raise HTTPException(status_code=404, detail="Institution not found")

        # Get the most recent tuition data for this institution
        tuition_data = (
            db.query(TuitionData)
            .filter(TuitionData.ipeds_id == ipeds_id)
            .order_by(TuitionData.academic_year.desc())
            .first()
        )

        if not tuition_data:
            return {
                "ipeds_id": ipeds_id,
                "institution_name": institution.name,
                "has_cost_data": False,
                "message": "No cost data available for this institution",
            }

        # Build response with all available cost data
        response = {
            "ipeds_id": ipeds_id,
            "institution_name": institution.name,
            "has_cost_data": True,
            "academic_year": tuition_data.academic_year,
            "data_source": tuition_data.data_source,
            # Tuition
            "tuition_in_state": tuition_data.tuition_in_state,
            "tuition_out_state": tuition_data.tuition_out_state,
            # Fees
            "required_fees_in_state": tuition_data.required_fees_in_state,
            "required_fees_out_state": tuition_data.required_fees_out_state,
            # Living expenses
            "room_board_on_campus": tuition_data.room_board_on_campus,
            # Timestamps
            "created_at": (
                tuition_data.created_at.isoformat() if tuition_data.created_at else None
            ),
            "updated_at": (
                tuition_data.updated_at.isoformat() if tuition_data.updated_at else None
            ),
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching costs for institution {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cost data")


@router.get("/institution/{ipeds_id}/summary")
async def get_institution_costs_summary(
    ipeds_id: int,
    residency: str = "in_state",  # or "out_of_state"
    db: Session = Depends(get_db),
):
    """
    Get a simplified cost summary for an institution.
    Useful for card displays and quick comparisons.
    """
    try:
        # Get institution
        institution = (
            db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
        )

        if not institution:
            raise HTTPException(status_code=404, detail="Institution not found")

        # Get tuition data
        tuition_data = (
            db.query(TuitionData)
            .filter(TuitionData.ipeds_id == ipeds_id)
            .order_by(TuitionData.academic_year.desc())
            .first()
        )

        if not tuition_data:
            return {
                "ipeds_id": ipeds_id,
                "institution_name": institution.name,
                "has_data": False,
            }

        # Calculate totals based on residency
        is_in_state = residency == "in_state"

        tuition = (
            tuition_data.tuition_in_state
            if is_in_state
            else tuition_data.tuition_out_state
        )
        fees = (
            tuition_data.required_fees_in_state
            if is_in_state
            else tuition_data.required_fees_out_state
        )
        room_board = tuition_data.room_board_on_campus

        # Calculate estimated total
        total_cost = 0
        if tuition:
            total_cost += tuition
        if fees:
            total_cost += fees
        if room_board:
            total_cost += room_board

        return {
            "ipeds_id": ipeds_id,
            "institution_name": institution.name,
            "academic_year": tuition_data.academic_year,
            "residency_status": residency,
            "has_data": True,
            "tuition": tuition,
            "fees": fees,
            "room_and_board": room_board,
            "estimated_total": total_cost if total_cost > 0 else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cost summary for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cost summary")


@router.get("/compare")
async def compare_institution_costs(
    ipeds_ids: str,  # Comma-separated list of IPEDS IDs
    residency: str = "in_state",
    db: Session = Depends(get_db),
):
    """
    Compare costs across multiple institutions.
    Example: /api/v1/costs/compare?ipeds_ids=102580,103501,442523&residency=in_state
    """
    try:
        # Parse IPEDS IDs
        ipeds_list = [int(id.strip()) for id in ipeds_ids.split(",")]

        if len(ipeds_list) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 institutions can be compared at once",
            )

        results = []

        for ipeds_id in ipeds_list:
            # Get institution
            institution = (
                db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
            )

            if not institution:
                continue

            # Get tuition data
            tuition_data = (
                db.query(TuitionData)
                .filter(TuitionData.ipeds_id == ipeds_id)
                .order_by(TuitionData.academic_year.desc())
                .first()
            )

            if not tuition_data:
                results.append(
                    {"ipeds_id": ipeds_id, "name": institution.name, "has_data": False}
                )
                continue

            # Get appropriate costs based on residency
            is_in_state = residency == "in_state"
            tuition = (
                tuition_data.tuition_in_state
                if is_in_state
                else tuition_data.tuition_out_state
            )
            fees = (
                tuition_data.required_fees_in_state
                if is_in_state
                else tuition_data.required_fees_out_state
            )

            # Calculate combined tuition + fees
            tuition_fees_combined = 0
            if tuition:
                tuition_fees_combined += tuition
            if fees:
                tuition_fees_combined += fees

            results.append(
                {
                    "ipeds_id": ipeds_id,
                    "name": institution.name,
                    "state": institution.state,
                    "control_type": (
                        institution.control_type.value
                        if institution.control_type
                        else None
                    ),
                    "has_data": True,
                    "academic_year": tuition_data.academic_year,
                    "tuition": tuition,
                    "fees": fees,
                    "tuition_fees_combined": (
                        tuition_fees_combined if tuition_fees_combined > 0 else None
                    ),
                    "room_board": tuition_data.room_board_on_campus,
                }
            )

        return {
            "residency_status": residency,
            "institutions": results,
            "count": len(results),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing institution costs: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare costs")
