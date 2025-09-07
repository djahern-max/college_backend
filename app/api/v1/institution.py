# app/api/v1/institutions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionResponse

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution_by_id(institution_id: int, db: Session = Depends(get_db)):
    """Get institution by ID"""
    try:
        institution = (
            db.query(Institution).filter(Institution.id == institution_id).first()
        )

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with ID {institution_id} not found",
            )

        return InstitutionResponse.model_validate(institution)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting institution {institution_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institution: {str(e)}",
        )
