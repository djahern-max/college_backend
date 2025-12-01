# app/api/v1/scholarships.py
# FIXED: Proper route ordering - specific routes BEFORE generic routes
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.models.scholarship import Scholarship, ScholarshipStatus
from app.schemas.scholarship import ScholarshipResponse

router = APIRouter()


# ============================================================================
# IMPORTANT: Route order matters!
# Put specific routes BEFORE generic catch-all routes
# ============================================================================


# Specific route must come BEFORE the catch-all /{scholarship_id}
@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
async def get_scholarship(scholarship_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single scholarship by ID.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Scholarship).where(Scholarship.id == scholarship_id)
    result = await db.execute(query)
    scholarship = result.scalar_one_or_none()

    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    return scholarship


# This MUST be last - it's the most generic route
@router.get("/")
async def get_scholarships(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(48, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Only show active scholarships"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated scholarships.
    PUBLIC endpoint - no authentication required.

    Query params:
    - page: Page number (default: 1)
    - limit: Items per page (default: 48, max: 100)
    - active_only: Filter to only active scholarships (default: true)
    """
    try:
        # Calculate offset from page number
        offset = (page - 1) * limit

        # Build base query
        query = select(Scholarship)

        # FIXED: Use 'status' field instead of 'is_active'
        if active_only:
            query = query.where(Scholarship.status == ScholarshipStatus.ACTIVE)

        # Get total count for pagination
        count_query = select(func.count()).select_from(Scholarship)
        if active_only:
            count_query = count_query.where(
                Scholarship.status == ScholarshipStatus.ACTIVE
            )

        total_result = await db.execute(count_query)
        total = total_result.scalar()  # FIXED: Use scalar() for single value

        # Sort by title
        query = query.order_by(Scholarship.title)

        # Apply pagination
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        scholarships = result.scalars().all()  # Use scalars() for list of objects

        # Calculate pagination metadata
        total_pages = (total + limit - 1) // limit  # Ceiling division

        return {
            "items": [ScholarshipResponse.model_validate(sch) for sch in scholarships],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_more": page < total_pages,
        }

    except Exception as e:
        # Log the error for debugging
        print(f"Error searching scholarships: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to search scholarships: {str(e)}"
        )
