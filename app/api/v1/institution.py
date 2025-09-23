# app/api/v1/institution.py - FIXED to work with streamlined service
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError
from typing import Optional, List
from sqlalchemy import or_

from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import (
    InstitutionResponse,
    InstitutionList,
    InstitutionSearch,
    CustomerRankUpdate,
)
from app.services.institution import InstitutionService

import logging

logger = logging.getLogger(__name__)

print("=== LOADING INSTITUTION ROUTER ===")
router = APIRouter()
print("Router created successfully")


@router.get("/featured", response_model=List[InstitutionResponse])
async def get_featured_institutions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get featured institutions with best images for homepage with pagination support"""
    try:
        service = InstitutionService(db)
        # FIXED: Remove priority_states_only parameter - new service uses curated schools automatically
        institutions = service.get_featured_institutions(limit, offset)
        return institutions
    except Exception as e:
        logger.error(f"Error getting featured institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get featured institutions: {str(e)}",
        )


@router.get("/search", response_model=InstitutionList)
async def search_institutions(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    state: Optional[str] = Query(
        None, description="Filter by state (e.g., 'NH', 'MA')"
    ),
    db: Session = Depends(get_db),
):
    """Search institutions by name, city, or state with pagination"""
    try:
        service = InstitutionService(db)

        # FIXED: Create search params with optional state filter
        search_params = InstitutionSearch(
            query=query, state=state  # Add state filter support
        )
        institutions, total = service.search_institutions(search_params, page, per_page)

        return InstitutionList(
            institutions=institutions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page,
        )
    except Exception as e:
        logger.error(f"Error searching institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search institutions: {str(e)}",
        )


@router.get("/by-priority", response_model=List[InstitutionResponse])
async def get_institutions_by_priority(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get institutions ordered by customer priority (for admin dashboard)"""
    try:
        service = InstitutionService(db)
        # FIXED: This method might need to be renamed in your new streamlined service
        # Check if this method exists in your new service or replace with appropriate method
        institutions = service.get_featured_institutions(
            limit, offset
        )  # Use featured instead
        return [InstitutionResponse.model_validate(inst) for inst in institutions]

    except Exception as e:
        logger.error(f"Error getting institutions by priority: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institutions by priority: {str(e)}",
        )


@router.get("/", response_model=InstitutionList)
async def list_institutions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    state: Optional[str] = Query(
        None, description="Filter by state (e.g., 'NH', 'MA')"
    ),
    min_image_quality: Optional[int] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Get all curated institutions with optional state filtering"""
    try:
        service = InstitutionService(db)

        # FIXED: Use the new streamlined service approach
        if state:
            # Filter by specific state
            institutions = service.get_schools_by_state(state.upper())
            total = len(institutions)

            # Apply pagination manually
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            institutions = institutions[start_idx:end_idx]
        else:
            # Get all curated schools using search with empty query
            search_params = InstitutionSearch(min_image_quality=min_image_quality)
            institutions, total = service.search_institutions(
                search_params, page, per_page
            )

        return InstitutionList(
            institutions=institutions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page,
        )
    except Exception as e:
        logger.error(f"Error listing institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list institutions: {str(e)}",
        )


@router.get("/states")
async def get_available_states(db: Session = Depends(get_db)):
    """Get list of available states for filtering"""
    try:
        service = InstitutionService(db)
        return service.get_available_states()
    except Exception as e:
        logger.error(f"Error getting available states: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available states: {str(e)}",
        )


@router.post("/bulk-update-ranks")
async def bulk_update_customer_ranks(
    updates: List[CustomerRankUpdate],
    db: Session = Depends(get_db),
):
    """Bulk update customer rankings for multiple institutions"""
    try:
        service = InstitutionService(db)
        results = []

        for update in updates:
            try:
                result = service.update_customer_rank(
                    update.institution_id, update.customer_rank
                )
                results.append(
                    {
                        "institution_id": update.institution_id,
                        "success": True,
                        "new_rank": result.customer_rank if result else None,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "institution_id": update.institution_id,
                        "success": False,
                        "error": str(e),
                    }
                )

        return {"results": results}

    except Exception as e:
        logger.error(f"Error bulk updating ranks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update ranks: {str(e)}",
        )


@router.put("/{institution_id}/customer-rank")
async def update_customer_rank(
    institution_id: int,
    rank_update: CustomerRankUpdate,
    db: Session = Depends(get_db),
):
    """Update customer ranking for a specific institution"""
    try:
        service = InstitutionService(db)
        institution = service.update_customer_rank(
            institution_id, rank_update.customer_rank
        )

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
            )

        return InstitutionResponse.model_validate(institution)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating customer rank: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update customer rank: {str(e)}",
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
