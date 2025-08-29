# app/api/v1/scholarships.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.scholarship import ScholarshipService
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipUpdate,
    ScholarshipResponse,
    ScholarshipSearchFilter,
    ScholarshipMatchResponse,
    ScholarshipMatchUpdate,
    ScholarshipMatchSummary,
    ScholarshipStatistics,
    BulkScholarshipCreate,
    BulkMatchingRequest,
    BulkMatchingResponse,
    ScholarshipVerificationUpdate,
)

router = APIRouter()


# ===========================
# SCHOLARSHIP CRUD OPERATIONS
# ===========================


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ScholarshipResponse
)
async def create_scholarship(
    scholarship_data: ScholarshipCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new scholarship (Admin only for now)"""
    try:
        service = ScholarshipService(db)
        scholarship = service.create_scholarship(
            scholarship_data, created_by_user_id=current_user["id"]
        )
        return ScholarshipResponse.model_validate(scholarship)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scholarship: {str(e)}",
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


@router.get("/", response_model=dict)
async def search_scholarships(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    scholarship_type: Optional[str] = None,
    active_only: bool = True,
    verified_only: bool = False,
    search_query: Optional[str] = None,
    min_amount: Optional[int] = Query(None, ge=0),
    max_amount: Optional[int] = Query(None, ge=0),
    student_gpa: Optional[float] = Query(None, ge=0.0, le=5.0),
    student_state: Optional[str] = None,
    student_major: Optional[str] = None,
    requires_essay: Optional[bool] = None,
    deadline_after: Optional[str] = None,
    sort_by: str = Query(
        "created_at", regex="^(match_score|deadline|amount|created_at|title)$"
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """Search and filter scholarships"""
    try:
        # Build search filter
        filters = ScholarshipSearchFilter(
            page=page,
            limit=limit,
            scholarship_type=scholarship_type,
            active_only=active_only,
            verified_only=verified_only,
            search_query=search_query,
            min_amount=min_amount,
            max_amount=max_amount,
            student_gpa=student_gpa,
            student_state=student_state,
            student_major=student_major,
            requires_essay=requires_essay,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search scholarships: {str(e)}",
        )


@router.patch("/{scholarship_id}", response_model=ScholarshipResponse)
async def update_scholarship(
    scholarship_id: int,
    scholarship_data: ScholarshipUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a scholarship (Admin only for now)"""
    try:
        service = ScholarshipService(db)
        scholarship = service.update_scholarship(scholarship_id, scholarship_data)

        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
            )

        return ScholarshipResponse.model_validate(scholarship)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scholarship: {str(e)}",
        )


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scholarship(
    scholarship_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a scholarship (Admin only for now)"""
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


# ===========================
# MATCHING ENDPOINTS
# ===========================


@router.get("/matches/me", response_model=dict)
async def get_my_matches(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scholarship matches for the current user"""
    try:
        service = ScholarshipService(db)
        matches, total = service.get_user_matches(
            current_user["id"], page=page, limit=limit, min_score=min_score
        )

        # Calculate pagination metadata
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "matches": [
                ScholarshipMatchResponse.model_validate(match) for match in matches
            ],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
                "items_per_page": limit,
                "has_next": has_next,
                "has_previous": has_prev,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get matches: {str(e)}",
        )


@router.post("/matches/calculate")
async def calculate_matches(
    force_recalculate: bool = Query(False),
    min_score: float = Query(30.0, ge=0.0, le=100.0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Calculate/recalculate scholarship matches for the current user"""
    try:
        service = ScholarshipService(db)
        matches_created = service.calculate_and_store_matches(
            current_user["id"], force_recalculate=force_recalculate, min_score=min_score
        )

        return {
            "message": "Matches calculated successfully",
            "matches_created": matches_created,
            "user_id": current_user["id"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate matches: {str(e)}",
        )


@router.patch("/matches/{scholarship_id}")
async def update_match_status(
    scholarship_id: int,
    status_data: ScholarshipMatchUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user's interaction status with a scholarship match"""
    try:
        service = ScholarshipService(db)
        updated_match = service.update_match_status(
            current_user["id"], scholarship_id, status_data
        )

        if not updated_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
            )

        return ScholarshipMatchResponse.model_validate(updated_match)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update match status: {str(e)}",
        )


@router.get("/matches/summary", response_model=ScholarshipMatchSummary)
async def get_match_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get summary statistics for the current user's matches"""
    try:
        service = ScholarshipService(db)
        summary = service.get_match_summary(current_user["id"])
        return summary

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match summary: {str(e)}",
        )


# ===========================
# STATISTICS & ANALYTICS
# ===========================


@router.get("/stats/platform", response_model=ScholarshipStatistics)
async def get_platform_statistics(db: Session = Depends(get_db)):
    """Get platform-wide scholarship statistics"""
    try:
        service = ScholarshipService(db)
        stats = service.get_scholarship_statistics()
        return ScholarshipStatistics(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )


@router.get("/expiring", response_model=List[ScholarshipResponse])
async def get_expiring_scholarships(
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get scholarships expiring within the specified number of days"""
    try:
        service = ScholarshipService(db)
        expiring_scholarships = service.get_expiring_scholarships(days_ahead)

        return [
            ScholarshipResponse.model_validate(scholarship)
            for scholarship in expiring_scholarships
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expiring scholarships: {str(e)}",
        )


# ===========================
# BULK OPERATIONS (Admin)
# ===========================


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
            bulk_data.scholarships, created_by_user_id=current_user["id"]
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


@router.post("/bulk/recalculate-matches", response_model=BulkMatchingResponse)
async def recalculate_all_matches(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recalculate matches for all users (Admin only)"""
    try:
        service = ScholarshipService(db)
        result = service.recalculate_all_matches()
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk recalculation failed: {str(e)}",
        )


@router.post("/maintenance/update-expired")
async def update_expired_scholarships(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update expired scholarships status (Admin maintenance task)"""
    try:
        service = ScholarshipService(db)
        updated_count = service.update_expired_scholarships()

        return {
            "message": "Expired scholarships updated",
            "updated_count": updated_count,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update expired scholarships: {str(e)}",
        )


# ===========================
# ADMIN VERIFICATION
# ===========================


@router.patch("/{scholarship_id}/verify")
async def verify_scholarship(
    scholarship_id: int,
    verification_data: ScholarshipVerificationUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verify or unverify a scholarship (Admin only)"""
    try:
        service = ScholarshipService(db)
        scholarship = service.verify_scholarship(
            scholarship_id,
            verification_data.verified,
            verification_data.verification_notes,
        )

        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
            )

        # Update featured status if provided
        if verification_data.featured is not None:
            scholarship.featured = verification_data.featured
            db.commit()
            db.refresh(scholarship)

        return ScholarshipResponse.model_validate(scholarship)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify scholarship: {str(e)}",
        )


# ===========================
# ORGANIZATION-SPECIFIC ENDPOINTS
# ===========================


@router.get("/by-organization/{organization}", response_model=List[ScholarshipResponse])
async def get_scholarships_by_organization(
    organization: str,
    db: Session = Depends(get_db),
):
    """Get all scholarships from a specific organization"""
    try:
        service = ScholarshipService(db)
        scholarships = service.get_scholarships_by_organization(organization)

        return [
            ScholarshipResponse.model_validate(scholarship)
            for scholarship in scholarships
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scholarships by organization: {str(e)}",
        )


# ===========================
# USER RECOMMENDATIONS
# ===========================


@router.get("/recommendations/me", response_model=List[ScholarshipResponse])
async def get_my_recommendations(
    limit: int = Query(10, ge=1, le=50),
    min_score: float = Query(50.0, ge=0.0, le=100.0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get personalized scholarship recommendations for the current user"""
    try:
        service = ScholarshipService(db)
        matches = service.find_matches_for_user(
            current_user["id"], min_score=min_score, limit=limit
        )

        # Extract scholarships from the (scholarship, score) tuples
        scholarships = [match[0] for match in matches]

        return [
            ScholarshipResponse.model_validate(scholarship)
            for scholarship in scholarships
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}",
        )
