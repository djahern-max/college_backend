# app/api/v1/institution.py - CLEANED UP
"""
Simplified institutions API - only uses fields that exist in the model
Removed all references to dropped fields (customer_rank, image_quality, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func

from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import (
    InstitutionResponse,
    InstitutionList,
    InstitutionSearchFilter,
)
from app.services.institution import InstitutionService

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=InstitutionList)
async def list_institutions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    state: Optional[str] = Query(None, min_length=2, max_length=2),
    control_type: Optional[str] = None,
    search_query: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all institutions with optional filtering"""
    try:
        service = InstitutionService(db)

        # Build search filter
        filters = InstitutionSearchFilter(
            page=page,
            limit=limit,
            state=state,
            control_type=control_type,
            search_query=search_query,
        )

        institutions, total = service.search_institutions(filters)

        return InstitutionList(
            institutions=[InstitutionResponse.model_validate(i) for i in institutions],
            total=total,
            page=page,
            limit=limit,
            has_more=page * limit < total,
        )

    except Exception as e:
        logger.error(f"Error listing institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list institutions: {str(e)}",
        )


@router.get("/search", response_model=InstitutionList)
async def search_institutions(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    state: Optional[str] = Query(None, min_length=2, max_length=2),
    db: Session = Depends(get_db),
):
    """Search institutions by name or city"""
    try:
        service = InstitutionService(db)

        filters = InstitutionSearchFilter(
            page=page,
            limit=limit,
            state=state,
            search_query=query,
        )

        institutions, total = service.search_institutions(filters)

        return InstitutionList(
            institutions=[InstitutionResponse.model_validate(i) for i in institutions],
            total=total,
            page=page,
            limit=limit,
            has_more=page * limit < total,
        )

    except Exception as e:
        logger.error(f"Error searching institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search institutions: {str(e)}",
        )


@router.get("/states", response_model=List[str])
async def get_available_states(db: Session = Depends(get_db)):
    """Get list of states that have institutions"""
    try:
        service = InstitutionService(db)
        states = service.get_available_states()
        return states

    except Exception as e:
        logger.error(f"Error getting available states: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available states: {str(e)}",
        )


@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific institution by ID"""
    try:
        service = InstitutionService(db)
        institution = service.get_institution_by_id(institution_id)

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
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


@router.get("/stats/summary", response_model=dict)
async def get_institution_stats(db: Session = Depends(get_db)):
    """Get institution statistics"""
    try:
        service = InstitutionService(db)

        total = db.query(Institution).count()
        by_state = {}
        by_control = {}

        # Get counts by state
        states = (
            db.query(Institution.state, func.count(Institution.id))
            .group_by(Institution.state)
            .all()
        )
        by_state = {state: count for state, count in states}

        # Get counts by control type
        controls = (
            db.query(Institution.control_type, func.count(Institution.id))
            .group_by(Institution.control_type)
            .all()
        )
        by_control = {str(ctrl): count for ctrl, count in controls}

        return {
            "total_institutions": total,
            "by_state": by_state,
            "by_control_type": by_control,
        }

    except Exception as e:
        logger.error(f"Error getting institution stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )
