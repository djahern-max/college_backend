# app/api/v1/scholarships.py
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

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
)

router = APIRouter()


# ===========================
# PUBLIC ENDPOINTS
# ===========================


@router.get("/", response_model=List[ScholarshipResponse])
async def get_scholarships(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Get paginated list of scholarships"""
    scholarship_service = ScholarshipService(db)
    scholarships, total = scholarship_service.get_scholarships_paginated(
        page=page, limit=limit, active_only=active_only
    )

    return scholarships


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
async def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    """Get scholarship by ID"""
    scholarship_service = ScholarshipService(db)
    scholarship = scholarship_service.get_scholarship_by_id(scholarship_id)

    if not scholarship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
        )

    return scholarship


@router.post("/search", response_model=List[ScholarshipResponse])
async def search_scholarships(
    filters: ScholarshipSearchFilter, db: Session = Depends(get_db)
):
    """Search scholarships with filters"""
    scholarship_service = ScholarshipService(db)
    scholarships, total = scholarship_service.search_scholarships(filters)

    return scholarships


@router.get("/statistics/platform")
async def get_platform_statistics(db: Session = Depends(get_db)):
    """Get platform-wide scholarship statistics"""
    scholarship_service = ScholarshipService(db)
    return scholarship_service.get_scholarship_statistics()


# ===========================
# USER-SPECIFIC ENDPOINTS
# ===========================


@router.get("/my/matches", response_model=List[ScholarshipMatchResponse])
async def get_my_matches(
    limit: int = Query(50, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's scholarship matches"""
    scholarship_service = ScholarshipService(db)
    matches = scholarship_service.get_user_matches(
        user_id=current_user["id"], limit=limit, min_score=min_score
    )

    return matches


@router.get("/my/summary", response_model=ScholarshipMatchSummary)
async def get_my_match_summary(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's scholarship match summary"""
    scholarship_service = ScholarshipService(db)
    return scholarship_service.get_match_summary(current_user["id"])


@router.post("/my/calculate-matches")
async def calculate_my_matches(
    force_recalculate: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Calculate scholarship matches for current user"""
    scholarship_service = ScholarshipService(db)
    matches_created = scholarship_service.calculate_and_store_matches(
        user_id=current_user["id"], force_recalculate=force_recalculate
    )

    return {
        "message": f"Successfully calculated matches",
        "matches_created": matches_created,
        "user_id": current_user["id"],
    }


@router.patch("/my/matches/{scholarship_id}", response_model=ScholarshipMatchResponse)
async def update_my_match_status(
    scholarship_id: int,
    status_data: ScholarshipMatchUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user's interaction with a scholarship match"""
    scholarship_service = ScholarshipService(db)
    updated_match = scholarship_service.update_match_status(
        user_id=current_user["id"],
        scholarship_id=scholarship_id,
        status_data=status_data,
    )

    if not updated_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship match not found"
        )

    return updated_match


# ===========================
# ADMIN ENDPOINTS
# ===========================


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ScholarshipResponse
)
async def create_scholarship(
    scholarship_data: ScholarshipCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new scholarship (admin only)"""
    # TODO: Add admin authorization check
    scholarship_service = ScholarshipService(db)
    scholarship = scholarship_service.create_scholarship(
        scholarship_data, created_by_user_id=current_user["id"]
    )

    return scholarship


@router.patch("/{scholarship_id}", response_model=ScholarshipResponse)
async def update_scholarship(
    scholarship_id: int,
    scholarship_data: ScholarshipUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update scholarship (admin only)"""
    # TODO: Add admin authorization check
    scholarship_service = ScholarshipService(db)
    scholarship = scholarship_service.update_scholarship(
        scholarship_id, scholarship_data
    )

    if not scholarship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
        )

    return scholarship


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scholarship(
    scholarship_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete scholarship (admin only)"""
    # TODO: Add admin authorization check
    scholarship_service = ScholarshipService(db)
    deleted = scholarship_service.delete_scholarship(scholarship_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found"
        )


@router.post("/admin/recalculate-all-matches")
async def recalculate_all_matches(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Recalculate matches for all users (admin only)"""
    # TODO: Add admin authorization check
    scholarship_service = ScholarshipService(db)
    result = scholarship_service.recalculate_all_matches()

    return {"message": "Successfully recalculated all matches", **result}


@router.get("/user/{user_id}/matches", response_model=List[ScholarshipMatchResponse])
async def get_user_matches(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scholarship matches for a specific user (admin only)"""
    # TODO: Add admin authorization check
    scholarship_service = ScholarshipService(db)
    matches = scholarship_service.get_user_matches(
        user_id=user_id, limit=limit, min_score=min_score
    )

    return matches


@router.get("/user/{user_id}/summary", response_model=ScholarshipMatchSummary)
async def get_user_match_summary(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scholarship match summary for a specific user (admin only)"""
    # TODO: Add admin authorization check
    scholarship_service = ScholarshipService(db)
    return scholarship_service.get_match_summary(user_id)


# ===========================
# CONVENIENCE ENDPOINTS
# ===========================


@router.get("/types/list")
async def get_scholarship_types():
    """Get list of available scholarship types"""
    from app.models.scholarship import ScholarshipType

    return [
        {"value": type_val.value, "label": type_val.value.replace("_", " ").title()}
        for type_val in ScholarshipType
    ]


@router.get("/my/quick-matches")
async def get_quick_matches(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get a quick list of top matches for dashboard display"""
    scholarship_service = ScholarshipService(db)
    matches = scholarship_service.get_user_matches(
        user_id=current_user["id"], limit=10, min_score=60.0
    )

    # Return simplified format for dashboard
    return [
        {
            "id": match.scholarship.id,
            "title": match.scholarship.title,
            "provider": match.scholarship.provider,
            "amount": match.scholarship.get_amount_display(),
            "deadline": match.scholarship.deadline,
            "match_score": match.match_score,
            "viewed": match.viewed,
            "bookmarked": match.bookmarked,
        }
        for match in matches
    ]
