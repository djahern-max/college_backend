# app/api/v1/institution.py
# FIXED: Proper route ordering - specific routes BEFORE generic routes
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionResponse

# No prefix - main.py already adds /api/v1/institutions
router = APIRouter()


# ============================================================================
# IMPORTANT: Route order matters!
# Put specific routes (like /by-id/{id}) BEFORE generic catch-all routes
# ============================================================================


@router.get("/by-id/{institution_id}", response_model=InstitutionResponse)
async def get_institution_by_id(
    institution_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a single institution by database ID.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


# This must come AFTER /by-id/{institution_id} but BEFORE the catch-all /
@router.get("/{ipeds_id}", response_model=InstitutionResponse)
async def get_institution(ipeds_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single institution by IPEDS ID.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution).where(Institution.ipeds_id == ipeds_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


# This MUST be last - it's the most generic route
@router.get("/")
async def get_institutions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(48, ge=1, le=100, description="Items per page"),
    state: Optional[str] = Query(
        None, max_length=2, description="Filter by state code"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated institutions with optional state filter.
    Returns institutions sorted by data completeness score.
    PUBLIC endpoint - no authentication required.

    Query params:
    - page: Page number (default: 1)
    - limit: Items per page (default: 48, max: 100)
    - state: Optional 2-letter state code filter
    """
    # Calculate offset from page number
    offset = (page - 1) * limit

    # Build base query
    query = select(Institution)

    # Apply state filter if provided
    if state:
        query = query.where(Institution.state == state.upper())

    # Get total count for pagination
    count_query = select(func.count()).select_from(Institution)
    if state:
        count_query = count_query.where(Institution.state == state.upper())

    # Execute count query without streaming
    result = await db.execute(count_query)
    total = result.scalar()  # Get the count value

    # Sort by data completeness score (best schools first), then name
    query = query.order_by(Institution.data_completeness_score.desc(), Institution.name)

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute institutions query
    institutions_result = await db.execute(query)
    institutions = (
        institutions_result.scalars().all()
    )  # Use scalars() for list of objects

    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit  # Ceiling division

    # Clean up institution data - remove invalid default image URLs
    items = []
    for inst in institutions:
        inst_dict = InstitutionResponse.model_validate(inst).model_dump()
        # Remove the problematic default image URL
        if inst_dict.get("primary_image_url") == "/images/default-institution.jpg":
            inst_dict["primary_image_url"] = None
        items.append(inst_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_more": page < total_pages,
    }
