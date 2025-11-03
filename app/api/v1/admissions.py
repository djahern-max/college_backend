# app/api/v1/admissions.py
"""
API endpoints for admissions data
Follows the service layer pattern used in the codebase
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.admissions import AdmissionsService
from app.schemas.admissions import AdmissionsDataResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/institution/{ipeds_id}", response_model=AdmissionsDataResponse)
async def get_institution_admissions(
    ipeds_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the most recent admissions data for a specific institution by IPEDS ID.

    Returns admissions statistics including:
    - Acceptance rate
    - Application numbers
    - SAT/ACT score ranges
    - Test submission percentages

    Args:
        ipeds_id: IPEDS institution identifier
        db: Database session

    Returns:
        AdmissionsDataResponse with latest admissions data

    Raises:
        404: If no admissions data found for this institution
        500: If database error occurs
    """
    try:
        admissions = AdmissionsService.get_latest_by_ipeds(db, ipeds_id)

        if not admissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No admissions data found for institution with IPEDS ID {ipeds_id}",
            )

        return AdmissionsDataResponse.model_validate(admissions)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admissions data for IPEDS {ipeds_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admissions data: {str(e)}",
        )


@router.get("/institution/{ipeds_id}/all", response_model=list[AdmissionsDataResponse])
async def get_institution_admissions_all_years(
    ipeds_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all admissions data (all academic years) for a specific institution by IPEDS ID.

    Useful for showing historical trends and year-over-year comparisons.
    Results are ordered by academic year (most recent first).

    Args:
        ipeds_id: IPEDS institution identifier
        db: Database session

    Returns:
        List of AdmissionsDataResponse for all available years

    Raises:
        404: If no admissions data found for this institution
        500: If database error occurs
    """
    try:
        admissions_data = AdmissionsService.get_all_by_ipeds(db, ipeds_id)

        if not admissions_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No admissions data found for institution with IPEDS ID {ipeds_id}",
            )

        return [AdmissionsDataResponse.model_validate(ad) for ad in admissions_data]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting all admissions data for IPEDS {ipeds_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admissions data: {str(e)}",
        )


@router.get(
    "/institution/{ipeds_id}/year/{academic_year}",
    response_model=AdmissionsDataResponse,
)
async def get_institution_admissions_by_year(
    ipeds_id: int,
    academic_year: str,
    db: Session = Depends(get_db),
):
    """
    Get admissions data for a specific institution and academic year.

    Args:
        ipeds_id: IPEDS institution identifier
        academic_year: Academic year (e.g., "2023-24" or "2023-2024")
        db: Database session

    Returns:
        AdmissionsDataResponse for the specified year

    Raises:
        404: If no admissions data found for this institution/year combination
        500: If database error occurs
    """
    try:
        admissions = AdmissionsService.get_by_academic_year(db, ipeds_id, academic_year)

        if not admissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No admissions data found for IPEDS ID {ipeds_id} in {academic_year}",
            )

        return AdmissionsDataResponse.model_validate(admissions)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting admissions for IPEDS {ipeds_id}, year {academic_year}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admissions data: {str(e)}",
        )
