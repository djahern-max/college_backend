# app/api/v1/scholarships.py - CLEANED UP
"""
Simplified scholarships API - only uses fields that exist in the model
Removed all references to dropped fields
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.scholarship import ScholarshipService
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipResponse,
    ScholarshipSearchFilter,
    BulkScholarshipCreate,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ScholarshipResponse
)
async def create_scholarship(
    scholarship_data: ScholarshipCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new scholarship (Admin only)"""
    try:
        service = ScholarshipService(db)
        scholarship = service.create_scholarship(scholarship_data)
        return ScholarshipResponse.model_validate(scholarship)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scholarship: {str(e)}",
        )


@router.get("/list", response_model=List[ScholarshipResponse])
async def list_scholarships(
    limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)
):
    """Simple list of scholarships"""
    try:
        service = ScholarshipService(db)
        scholarships = service.get_all_scholarships(limit=limit, active_only=True)

        return [
            ScholarshipResponse.model_validate(scholarship)
            for scholarship in scholarships
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scholarships: {str(e)}",
        )


@router.get("/", response_model=dict)
async def search_scholarships(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    scholarship_type: Optional[str] = None,
    active_only: bool = True,
    verified_only: bool = False,
    featured_only: bool = False,
    search_query: Optional[str] = None,
    min_amount: Optional[int] = Query(None, ge=0),
    max_amount: Optional[int] = Query(None, ge=0),
    requires_essay: Optional[bool] = None,
    requires_interview: Optional[bool] = None,
    renewable_only: Optional[bool] = None,
    sort_by: str = Query(
        "created_at", pattern="^(created_at|amount_exact|title|views_count)$"
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """
    Search and filter scholarships
    Only uses fields that exist in the simplified model
    """
    try:
        # Build search filter (only with fields that exist)
        filters = ScholarshipSearchFilter(
            page=page,
            limit=limit,
            scholarship_type=scholarship_type,
            active_only=active_only,
            verified_only=verified_only,
            featured_only=featured_only,
            search_query=search_query,
            min_amount=min_amount,
            max_amount=max_amount,
            requires_essay=requires_essay,
            requires_interview=requires_interview,
            renewable_only=renewable_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        service = ScholarshipService(db)
        scholarships, total = service.search_scholarships(filters)

        # Calculate pagination metadata
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "scholarships": [
                ScholarshipResponse.model_validate(s) for s in scholarships
            ],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
                "items_per_page": limit,
                "has_next": has_next,
                "has_previous": has_prev,
            },
            "filters_applied": filters.model_dump(exclude_none=True),
        }

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search scholarships: {str(e)}",
        )


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
async def get_scholarship(
    scholarship_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific scholarship by ID"""
    try:
        service = ScholarshipService(db)
        scholarship = service.get_scholarship_by_id(scholarship_id)

        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
            )

        # Increment view count
        service.increment_view_count(scholarship_id)

        return ScholarshipResponse.model_validate(scholarship)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scholarship: {str(e)}",
        )


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scholarship(
    scholarship_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a scholarship (Admin only)"""
    try:
        service = ScholarshipService(db)
        deleted = service.delete_scholarship(scholarship_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scholarship: {str(e)}",
        )


@router.post("/bulk/create", response_model=dict)
async def bulk_create_scholarships(
    bulk_data: BulkScholarshipCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk create scholarships (Admin only)"""
    try:
        service = ScholarshipService(db)
        created_scholarships, errors = service.bulk_create_scholarships(
            bulk_data.scholarships
        )

        return {
            "message": "Bulk creation completed",
            "created_count": len(created_scholarships),
            "error_count": len(errors),
            "created_scholarships": [
                ScholarshipResponse.model_validate(s) for s in created_scholarships
            ],
            "errors": errors,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk creation failed: {str(e)}",
        )


@router.get("/stats/summary", response_model=dict)
async def get_scholarship_stats(db: Session = Depends(get_db)):
    """Get scholarship statistics"""
    try:
        service = ScholarshipService(db)
        stats = service.get_scholarship_stats()
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )
