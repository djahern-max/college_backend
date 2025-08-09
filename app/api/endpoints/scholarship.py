from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipUpdate,
    ScholarshipResponse,
    ScholarshipSearch,
    ScholarshipSummary
)
from app.services.scholarship import ScholarshipService

router = APIRouter(
    prefix="/scholarships",
    tags=["scholarships"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/", 
    response_model=ScholarshipResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new scholarship",
    description="Create a new scholarship entry. Requires authentication."
)
async def create_scholarship(
    scholarship: ScholarshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new scholarship"""
    service = ScholarshipService(db)
    return await service.create_scholarship(scholarship)


@router.get(
    "/search",
    response_model=dict,
    summary="Search scholarships",
    description="Search scholarships with various filters and pagination"
)
async def search_scholarships(
    query: Optional[str] = Query(None, description="Search query for title/description"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    scholarship_type: Optional[str] = Query(None, description="Filter by scholarship type"),
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum award amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum award amount"),
    deadline_after: Optional[str] = Query(None, description="Deadline after this date (YYYY-MM-DD)"),
    deadline_before: Optional[str] = Query(None, description="Deadline before this date (YYYY-MM-DD)"),
    verified_only: bool = Query(False, description="Show only verified scholarships"),
    renewable_only: bool = Query(False, description="Show only renewable scholarships"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """Search scholarships with advanced filtering"""
    
    # Parse categories if provided
    categories_list = None
    if categories:
        categories_list = [cat.strip() for cat in categories.split(",")]
    
    # Parse dates if provided
    deadline_after_date = None
    deadline_before_date = None
    
    if deadline_after:
        try:
            deadline_after_date = datetime.strptime(deadline_after, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deadline_after format. Use YYYY-MM-DD"
            )
    
    if deadline_before:
        try:
            deadline_before_date = datetime.strptime(deadline_before, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deadline_before format. Use YYYY-MM-DD"
            )
    
    # Create search parameters
    search_params = ScholarshipSearch(
        query=query,
        provider=provider,
        scholarship_type=scholarship_type,
        categories=categories_list,
        min_amount=min_amount,
        max_amount=max_amount,
        deadline_after=deadline_after_date,
        deadline_before=deadline_before_date,
        verified_only=verified_only,
        renewable_only=renewable_only,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = ScholarshipService(db)
    results, total_count = await service.search_scholarships(search_params)
    
    return {
        "scholarships": results,
        "total_count": total_count,
        "page": skip // limit + 1,
        "per_page": limit,
        "total_pages": (total_count + limit - 1) // limit
    }


@router.get(
    "/active",
    response_model=List[ScholarshipSummary],
    summary="Get active scholarships",
    description="Get a list of active scholarships with pagination"
)
async def get_active_scholarships(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get active scholarships"""
    service = ScholarshipService(db)
    return await service.get_active_scholarships(limit, skip)


@router.get(
    "/expiring-soon",
    response_model=List[ScholarshipSummary],
    summary="Get scholarships expiring soon",
    description="Get scholarships with deadlines approaching within specified days"
)
async def get_expiring_scholarships(
    days: int = Query(30, ge=1, le=365, description="Number of days ahead to check"),
    db: Session = Depends(get_db)
):
    """Get scholarships expiring within specified days"""
    service = ScholarshipService(db)
    return await service.get_expiring_soon(days)


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get scholarship statistics",
    description="Get overview statistics about scholarships in the database"
)
async def get_scholarship_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get scholarship statistics"""
    service = ScholarshipService(db)
    return await service.get_statistics()


@router.get(
    "/provider/{provider_name}",
    response_model=List[ScholarshipSummary],
    summary="Get scholarships by provider",
    description="Get scholarships from a specific provider"
)
async def get_scholarships_by_provider(
    provider_name: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get scholarships by provider"""
    service = ScholarshipService(db)
    return await service.get_by_provider(provider_name, limit)


@router.get(
    "/categories/{categories}",
    response_model=List[ScholarshipSummary],
    summary="Get scholarships by categories",
    description="Get scholarships matching specific categories (comma-separated)"
)
async def get_scholarships_by_categories(
    categories: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get scholarships by categories"""
    categories_list = [cat.strip() for cat in categories.split(",")]
    service = ScholarshipService(db)
    return await service.get_by_categories(categories_list, limit)


@router.get(
    "/{scholarship_id}",
    response_model=ScholarshipResponse,
    summary="Get a specific scholarship",
    description="Get detailed information about a specific scholarship"
)
async def get_scholarship(
    scholarship_id: int,
    db: Session = Depends(get_db)
):
    """Get a scholarship by ID"""
    service = ScholarshipService(db)
    return await service.get_scholarship(scholarship_id)


@router.put(
    "/{scholarship_id}",
    response_model=ScholarshipResponse,
    summary="Update a scholarship",
    description="Update scholarship information. Requires authentication."
)
async def update_scholarship(
    scholarship_id: int,
    scholarship: ScholarshipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a scholarship"""
    service = ScholarshipService(db)
    return await service.update_scholarship(scholarship_id, scholarship)


@router.delete(
    "/{scholarship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a scholarship",
    description="Soft delete a scholarship by setting it to inactive. Requires authentication."
)
async def delete_scholarship(
    scholarship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a scholarship (soft delete)"""
    service = ScholarshipService(db)
    await service.delete_scholarship(scholarship_id)


@router.post(
    "/{scholarship_id}/verify",
    response_model=ScholarshipResponse,
    summary="Mark scholarship as verified",
    description="Mark a scholarship as manually verified. Requires authentication."
)
async def verify_scholarship(
    scholarship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark scholarship as verified"""
    service = ScholarshipService(db)
    return await service.mark_as_verified(scholarship_id)


@router.post(
    "/{scholarship_id}/apply",
    summary="Record scholarship application",
    description="Increment application count when a student applies"
)
async def record_application(
    scholarship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Record that someone applied for this scholarship"""
    service = ScholarshipService(db)
    success = await service.increment_application_count(scholarship_id)
    
    if success:
        return {"message": "Application recorded successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found"
        )


@router.post(
    "/bulk",
    response_model=List[ScholarshipResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple scholarships",
    description="Create multiple scholarships in one request. Requires authentication."
)
async def create_bulk_scholarships(
    scholarships: List[ScholarshipCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create multiple scholarships in bulk"""
    service = ScholarshipService(db)
    return await service.bulk_create_scholarships(scholarships)