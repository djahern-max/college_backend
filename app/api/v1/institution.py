# app/api/v1/institutions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionResponse
from pydantic import BaseModel

router = APIRouter(prefix="/institutions", tags=["institutions"])


class PaginatedInstitutionResponse(BaseModel):
    """Paginated response for institutions"""

    institutions: List[InstitutionResponse]
    total: int
    page: int
    limit: int
    has_more: bool


@router.get("", response_model=PaginatedInstitutionResponse)
async def get_institutions(
    state: Optional[str] = Query(None, max_length=2),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all institutions with pagination.

    Args:
        state: Optional state filter (2-letter code)
        page: Page number (starts at 1)
        limit: Results per page (max 500)
        db: Database session

    Returns:
        Paginated response with institutions, total count, and pagination info
    """
    # Build base query
    query = select(Institution)
    count_query = select(func.count(Institution.id))

    # Apply filters
    if state:
        state_upper = state.upper()
        query = query.where(Institution.state == state_upper)
        count_query = count_query.where(Institution.state == state_upper)

    # Get total count (for pagination metadata)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Priority states first (NH, MA, VT, NY, FL, CA), then alphabetical
    priority_states = ["NH", "MA", "VT", "NY", "FL", "CA"]
    if not state:
        # Custom sort: priority states first, then alphabetical
        query = query.order_by(Institution.state, Institution.name)
    else:
        query = query.order_by(Institution.name)

    # Apply pagination
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    institutions = result.scalars().all()

    # Calculate if there are more pages
    has_more = (offset + len(institutions)) < total

    return PaginatedInstitutionResponse(
        institutions=institutions,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


@router.get("/{ipeds_id}", response_model=InstitutionResponse)
async def get_institution(ipeds_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single institution by IPEDS ID"""
    query = select(Institution).where(Institution.ipeds_id == ipeds_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


@router.get("/by-id/{institution_id}", response_model=InstitutionResponse)
async def get_institution_by_id(
    institution_id: int, db: AsyncSession = Depends(get_db)
):
    """Get a single institution by database ID"""
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution
