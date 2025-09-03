# app/api/v1/colleges.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.college import CollegeService
from app.schemas.college import (
    CollegeCreate,
    CollegeUpdate,
    CollegeResponse,
    CollegeSearchFilter,
    CollegeMatchResponse,
    CollegeMatchUpdate,
    CollegeMatchSummary,
    CollegeBatchCreate,
    CollegeBatchResponse,
    CollegeStatistics,
    CollegeRecommendationRequest,
    CollegeRecommendationResponse,
)

router = APIRouter()

# ===========================
# COLLEGE CRUD OPERATIONS
# ===========================


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CollegeResponse)
async def create_college(
    college_data: CollegeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Admin only in production
):
    """Create a new college"""
    try:
        college_service = CollegeService(db)
        college = college_service.create_college(college_data)
        return CollegeResponse.model_validate(college)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create college: {str(e)}",
        )


@router.get("/{college_id}", response_model=CollegeResponse)
async def get_college(college_id: int, db: Session = Depends(get_db)):
    """Get college by ID"""
    college_service = CollegeService(db)
    college = college_service.get_college_by_id(college_id)

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="College not found"
        )

    if not college.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="College is no longer active"
        )

    return CollegeResponse.model_validate(college)


@router.patch("/{college_id}", response_model=CollegeResponse)
async def update_college(
    college_id: int,
    college_data: CollegeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Admin only in production
):
    """Update college information"""
    try:
        college_service = CollegeService(db)
        college = college_service.update_college(college_id, college_data)

        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found",
            )

        return CollegeResponse.model_validate(college)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update college: {str(e)}",
        )


@router.delete("/{college_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Admin only in production
):
    """Delete college (soft delete)"""
    try:
        college_service = CollegeService(db)
        deleted = college_service.delete_college(college_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete college: {str(e)}",
        )


@router.post("/batch", response_model=CollegeBatchResponse)
async def batch_create_colleges(
    batch_data: CollegeBatchCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Admin only in production
):
    """Batch create multiple colleges"""
    try:
        college_service = CollegeService(db)
        result = college_service.batch_create_colleges(batch_data.colleges)
        return CollegeBatchResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch create colleges: {str(e)}",
        )


# ===========================
# COLLEGE SEARCH AND FILTERING
# ===========================


@router.get("/", response_model=dict)
async def search_colleges(
    db: Session = Depends(get_db),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    # Basic filters
    active_only: bool = Query(True, description="Only active colleges"),
    verified_only: bool = Query(False, description="Only verified colleges"),
    # Search
    search_query: Optional[str] = Query(
        None, description="Search college names and locations"
    ),
    # Location
    state: Optional[str] = Query(None, description="Filter by state"),
    region: Optional[str] = Query(None, description="Filter by region"),
    campus_setting: Optional[str] = Query(
        None, description="Urban, Suburban, or Rural"
    ),
    # Institution type
    college_type: Optional[str] = Query(
        None, description="public, private_nonprofit, etc."
    ),
    college_size: Optional[str] = Query(None, description="small, medium, or large"),
    # Academic filters
    min_acceptance_rate: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_acceptance_rate: Optional[float] = Query(None, ge=0.0, le=1.0),
    admission_difficulty: Optional[str] = Query(
        None, description="Admission difficulty level"
    ),
    # Student profile (for matching)
    student_gpa: Optional[float] = Query(None, ge=0.0, le=5.0),
    student_sat_score: Optional[int] = Query(None, ge=400, le=1600),
    student_act_score: Optional[int] = Query(None, ge=1, le=36),
    student_major: Optional[str] = Query(None, description="Intended major"),
    student_state: Optional[str] = Query(None, description="Student's home state"),
    # Financial filters
    max_tuition_in_state: Optional[int] = Query(None, ge=0),
    max_tuition_out_of_state: Optional[int] = Query(None, ge=0),
    max_total_cost: Optional[int] = Query(None, ge=0),
    # Program filters
    strong_programs_only: Optional[bool] = Query(
        None, description="Only colleges with nationally recognized programs"
    ),
    # Size filters
    min_enrollment: Optional[int] = Query(None, ge=0),
    max_enrollment: Optional[int] = Query(None, ge=0),
    # Diversity filters
    historically_black: Optional[bool] = Query(None),
    hispanic_serving: Optional[bool] = Query(None),
    # Athletics
    athletic_division: Optional[str] = Query(None, description="D1, D2, D3, etc."),
    # Outcomes
    min_graduation_rate: Optional[float] = Query(None, ge=0.0, le=1.0),
    min_retention_rate: Optional[float] = Query(None, ge=0.0, le=1.0),
    # Sorting
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: str = Query("asc", description="asc or desc"),
):
    """Search and filter colleges with comprehensive options"""
    try:
        # Create filter object from query parameters
        filters = CollegeSearchFilter(
            page=page,
            limit=limit,
            active_only=active_only,
            verified_only=verified_only,
            search_query=search_query,
            state=state,
            region=region,
            campus_setting=campus_setting,
            college_type=college_type,
            college_size=college_size,
            min_acceptance_rate=min_acceptance_rate,
            max_acceptance_rate=max_acceptance_rate,
            admission_difficulty=admission_difficulty,
            student_gpa=student_gpa,
            student_sat_score=student_sat_score,
            student_act_score=student_act_score,
            student_major=student_major,
            student_state=student_state,
            max_tuition_in_state=max_tuition_in_state,
            max_tuition_out_of_state=max_tuition_out_of_state,
            max_total_cost=max_total_cost,
            strong_programs_only=strong_programs_only,
            min_enrollment=min_enrollment,
            max_enrollment=max_enrollment,
            historically_black=historically_black,
            hispanic_serving=hispanic_serving,
            athletic_division=athletic_division,
            min_graduation_rate=min_graduation_rate,
            min_retention_rate=min_retention_rate,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        college_service = CollegeService(db)
        colleges, total = college_service.search_colleges(filters)

        # Convert to response format
        college_responses = [
            CollegeResponse.model_validate(college) for college in colleges
        ]

        return {
            "colleges": college_responses,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
            "filters_applied": filters.model_dump(exclude_unset=True),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search colleges: {str(e)}",
        )


@router.get("/search/suggestions", response_model=List[CollegeResponse])
async def get_college_suggestions(
    query: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get college name suggestions for autocomplete"""
    try:
        college_service = CollegeService(db)
        colleges = college_service.search_colleges_by_name(query, limit)
        return [CollegeResponse.model_validate(college) for college in colleges]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get college suggestions: {str(e)}",
        )


@router.get("/by-state/{state}", response_model=List[CollegeResponse])
async def get_colleges_by_state(
    state: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get all colleges in a specific state"""
    try:
        college_service = CollegeService(db)
        colleges = college_service.get_colleges_by_state(state)[:limit]
        return [CollegeResponse.model_validate(college) for college in colleges]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get colleges by state: {str(e)}",
        )


@router.get("/{college_id}/similar", response_model=List[CollegeResponse])
async def get_similar_colleges(
    college_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get colleges similar to the specified college"""
    try:
        college_service = CollegeService(db)
        colleges = college_service.get_similar_colleges(college_id, limit)
        return [CollegeResponse.model_validate(college) for college in colleges]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get similar colleges: {str(e)}",
        )


# ===========================
# COLLEGE MATCHING AND RECOMMENDATIONS
# ===========================


@router.get("/matches/my-matches", response_model=List[CollegeMatchResponse])
async def get_my_college_matches(
    limit: int = Query(50, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get college matches for the current user"""
    try:
        college_service = CollegeService(db)
        matches = college_service.get_user_matches(current_user["id"], limit, min_score)
        return [CollegeMatchResponse.model_validate(match) for match in matches]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get college matches: {str(e)}",
        )


@router.post("/matches/calculate")
async def calculate_college_matches(
    force_recalculate: bool = Query(
        False, description="Force recalculation of existing matches"
    ),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Calculate and store college matches for the current user"""
    try:
        college_service = CollegeService(db)
        matches_created = college_service.calculate_and_store_matches(
            current_user["id"], force_recalculate
        )

        return {
            "message": "College matches calculated successfully",
            "matches_created": matches_created,
            "user_id": current_user["id"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate college matches: {str(e)}",
        )


@router.get("/matches/summary", response_model=CollegeMatchSummary)
async def get_college_match_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get summary of college matches for the current user"""
    try:
        college_service = CollegeService(db)
        summary = college_service.get_match_summary(current_user["id"])
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get college match summary: {str(e)}",
        )


@router.patch("/matches/{college_id}", response_model=CollegeMatchResponse)
async def update_college_match(
    college_id: int,
    match_data: CollegeMatchUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update interaction with a college match"""
    try:
        college_service = CollegeService(db)
        match = college_service.update_match_status(
            current_user["id"], college_id, match_data
        )

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College match not found",
            )

        return CollegeMatchResponse.model_validate(match)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update college match: {str(e)}",
        )


@router.post("/recommendations", response_model=CollegeRecommendationResponse)
async def get_college_recommendations(
    request: CollegeRecommendationRequest = CollegeRecommendationRequest(),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get personalized college recommendations"""
    try:
        college_service = CollegeService(db)
        user_id = request.user_id or current_user["id"]

        # Calculate matches if needed
        if request.force_recalculate:
            college_service.calculate_and_store_matches(user_id, force_recalculate=True)

        # Get matches
        all_matches = college_service.get_user_matches(user_id, limit=100)

        # Filter by category preferences
        filtered_matches = []
        for match in all_matches:
            if (
                (request.include_safety and match.match_category == "safety")
                or (request.include_match and match.match_category == "match")
                or (request.include_reach and match.match_category == "reach")
            ):
                filtered_matches.append(match)

        # Limit results
        recommendations = filtered_matches[: request.limit]

        # Get summary
        summary = college_service.get_match_summary(user_id)

        return CollegeRecommendationResponse(
            recommendations=[
                CollegeMatchResponse.model_validate(match) for match in recommendations
            ],
            summary=summary,
            total_colleges_analyzed=len(all_matches),
            recommendation_generated_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get college recommendations: {str(e)}",
        )


# ===========================
# STATISTICS AND ANALYTICS
# ===========================


@router.get("/statistics", response_model=CollegeStatistics)
async def get_college_statistics(db: Session = Depends(get_db)):
    """Get college platform statistics"""
    try:
        college_service = CollegeService(db)
        stats = college_service.get_college_statistics()
        return CollegeStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get college statistics: {str(e)}",
        )


# ===========================
# ADMIN OPERATIONS
# ===========================


@router.post("/matches/recalculate-all")
async def recalculate_all_college_matches(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Admin only in production
):
    """Recalculate matches for all users (admin only)"""
    try:
        college_service = CollegeService(db)
        result = college_service.recalculate_all_matches()

        return {
            "message": "Successfully recalculated all college matches",
            "users_processed": result["users_processed"],
            "total_matches_created": result["total_matches_created"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate all matches: {str(e)}",
        )


# ===========================
# UTILITY ENDPOINTS
# ===========================


@router.get("/filters/options")
async def get_filter_options(db: Session = Depends(get_db)):
    """Get available options for college filters"""
    try:
        college_service = CollegeService(db)

        # Get distinct values for various filter fields
        states = (
            db.query(College.state).distinct().filter(College.is_active == True).all()
        )
        regions = (
            db.query(College.region).distinct().filter(College.is_active == True).all()
        )
        campus_settings = (
            db.query(College.campus_setting)
            .distinct()
            .filter(College.is_active == True)
            .all()
        )
        athletic_divisions = (
            db.query(College.athletic_division)
            .distinct()
            .filter(College.is_active == True)
            .all()
        )

        return {
            "college_types": [
                "public",
                "private_nonprofit",
                "private_for_profit",
                "community_college",
            ],
            "college_sizes": ["small", "medium", "large"],
            "admission_difficulties": [
                "most_difficult",
                "very_difficult",
                "moderately_difficult",
                "minimally_difficult",
                "noncompetitive",
            ],
            "states": sorted([s[0] for s in states if s[0]]),
            "regions": sorted([r[0] for r in regions if r[0]]),
            "campus_settings": sorted([c[0] for c in campus_settings if c[0]]),
            "athletic_divisions": sorted([a[0] for a in athletic_divisions if a[0]]),
            "sort_options": [
                "name",
                "acceptance_rate",
                "tuition_in_state",
                "tuition_out_of_state",
                "total_enrollment",
                "graduation_rate_6_year",
                "us_news_ranking",
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get filter options: {str(e)}",
        )


@router.get("/health")
async def college_service_health():
    """Health check for college service"""
    return {
        "service": "college",
        "status": "healthy",
        "timestamp": datetime.utcnow(),
    }
