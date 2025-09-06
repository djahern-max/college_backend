# app/api/v1/colleges.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import func

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.college import CollegeService
from app.schemas.college import (
    CollegeCreate,
    CollegeUpdate,
    CollegeResponse,
    CollegeSearchFilters,
    CollegeSearchResponse,
    CollegeFavoriteCreate,
    CollegeFavoriteResponse,
    CollegeSavedSearchCreate,
    CollegeSavedSearchResponse,
    CollegeComparisonRequest,
    CollegeMatchRequest,
    CollegeMatchResponse,
    CollegeInsightsResponse,
    BulkCollegeCreate,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ===========================
# DEBUG ENDPOINTS (Add these first for testing)
# ===========================


@router.get("/debug/{college_id}", response_model=Dict[str, Any])
async def debug_college_data(college_id: int, db: Session = Depends(get_db)):
    """
    Debug endpoint to see ALL raw data for a specific college ID.
    Shows exactly what's in the database including null fields.
    """
    try:
        from app.models.college import College
        from sqlalchemy import inspect

        # Get the college record
        college = db.query(College).filter(College.id == college_id).first()

        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College with ID {college_id} not found",
            )

        # Get all column names from the model
        mapper = inspect(College)
        columns = [column.key for column in mapper.columns]

        # Build complete data dictionary with ALL fields
        college_data = {}
        for column in columns:
            value = getattr(college, column, None)

            # Convert special types to serializable format
            if hasattr(value, "value"):  # Enum values
                college_data[column] = value.value
            elif hasattr(value, "isoformat"):  # DateTime objects
                college_data[column] = value.isoformat()
            else:
                college_data[column] = value

        return {
            "college_id": college_id,
            "found": True,
            "data": college_data,
            "data_summary": {
                "total_fields": len(college_data),
                "non_null_fields": len(
                    [v for v in college_data.values() if v is not None]
                ),
                "null_fields": len([v for v in college_data.values() if v is None]),
            },
            "financial_data": {
                "tuition_in_state": college_data.get("tuition_in_state"),
                "tuition_out_state": college_data.get("tuition_out_state"),
                "total_cost_in_state": college_data.get("total_cost_in_state"),
                "total_cost_out_state": college_data.get("total_cost_out_state"),
                "room_and_board": college_data.get("room_and_board"),
                "required_fees": college_data.get("required_fees"),
            },
            "admissions_data": {
                "acceptance_rate": college_data.get("acceptance_rate"),
                "sat_total_25": college_data.get("sat_total_25"),
                "sat_total_75": college_data.get("sat_total_75"),
                "act_composite_25": college_data.get("act_composite_25"),
                "act_composite_75": college_data.get("act_composite_75"),
            },
            "basic_info": {
                "name": college_data.get("name"),
                "state": college_data.get("state"),
                "city": college_data.get("city"),
                "college_type": college_data.get("college_type"),
                "total_enrollment": college_data.get("total_enrollment"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug college data failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}",
        )


@router.get("/debug/summary", response_model=Dict[str, Any])
async def debug_database_summary(db: Session = Depends(get_db)):
    """
    Debug endpoint to see overall database state and field coverage.
    """
    try:
        from app.models.college import College
        from sqlalchemy import func, inspect

        # Get total count
        total_colleges = db.query(College).count()

        if total_colleges == 0:
            return {"total_colleges": 0, "message": "No colleges found in database"}

        # Get field coverage for key financial fields
        financial_fields = [
            "tuition_in_state",
            "tuition_out_state",
            "total_cost_in_state",
            "total_cost_out_state",
            "room_and_board",
            "required_fees",
        ]

        field_coverage = {}
        for field in financial_fields:
            count = (
                db.query(College).filter(getattr(College, field).isnot(None)).count()
            )
            field_coverage[field] = {
                "count": count,
                "percentage": round((count / total_colleges) * 100, 2),
            }

        # Get some sample college IDs
        sample_colleges = db.query(College.id, College.name).limit(5).all()

        # Check if any colleges have financial data
        has_any_financial = (
            db.query(College)
            .filter(
                (College.tuition_in_state.isnot(None))
                | (College.tuition_out_state.isnot(None))
                | (College.room_and_board.isnot(None))
            )
            .count()
        )

        return {
            "total_colleges": total_colleges,
            "has_any_financial_data": has_any_financial,
            "financial_field_coverage": field_coverage,
            "sample_college_ids": [
                {"id": c.id, "name": c.name} for c in sample_colleges
            ],
            "test_urls": [
                f"/api/v1/colleges/debug/{c.id}" for c in sample_colleges[:3]
            ],
        }

    except Exception as e:
        logger.error(f"Debug summary failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug summary failed: {str(e)}",
        )


# ===========================
# COLLEGE SEARCH ENDPOINTS
# ===========================


@router.get("/search", response_model=CollegeSearchResponse)
async def search_colleges(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    # Text search
    search_query: Optional[str] = Query(
        None, description="Search college names, cities"
    ),
    # Location filters
    state: Optional[str] = Query(
        None, description="Comma-separated state codes (CA,NY,TX)"
    ),
    city: Optional[str] = Query(None, description="City name"),
    region: Optional[str] = Query(None, description="Geographic region"),
    # Institution type
    college_type: Optional[str] = Query(None, description="Comma-separated types"),
    size_category: Optional[str] = Query(None, description="Comma-separated sizes"),
    carnegie_classification: Optional[str] = Query(
        None, description="Carnegie classification"
    ),
    # Special designations
    hbcu_only: bool = Query(False, description="HBCUs only"),
    hsi_only: bool = Query(False, description="Hispanic Serving Institutions only"),
    women_only: bool = Query(False, description="Women's colleges only"),
    religious_only: bool = Query(False, description="Religious institutions only"),
    # Enrollment
    min_enrollment: Optional[int] = Query(None, ge=0, description="Minimum enrollment"),
    max_enrollment: Optional[int] = Query(None, ge=0, description="Maximum enrollment"),
    # Academic filters
    min_acceptance_rate: Optional[float] = Query(None, ge=0, le=100),
    max_acceptance_rate: Optional[float] = Query(None, ge=0, le=100),
    # Student profile (for matching)
    student_gpa: Optional[float] = Query(None, ge=0, le=5, description="Student's GPA"),
    student_sat_score: Optional[int] = Query(None, ge=400, le=1600),
    student_act_score: Optional[int] = Query(None, ge=1, le=36),
    # Financial filters
    max_tuition: Optional[int] = Query(None, ge=0, description="Maximum tuition"),
    max_total_cost: Optional[int] = Query(None, ge=0, description="Maximum total cost"),
    in_state_student: bool = Query(False, description="In-state tuition rates"),
    # Programs
    major_interest: Optional[str] = Query(None, description="Intended major"),
    # Campus features
    urban_setting: bool = Query(False, description="Urban setting only"),
    requires_on_campus_housing: Optional[bool] = Query(None),
    ncaa_division: Optional[str] = Query(None, description="NCAA division"),
    test_optional_only: bool = Query(False, description="Test-optional only"),
    # Sorting
    sort_by: str = Query(
        "name",
        regex="^(name|acceptance_rate|tuition|enrollment|sat_score|graduation_rate|competitiveness|affordability|value)$",
    ),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """
    Advanced college search with comprehensive filtering options
    """
    try:
        # Parse comma-separated values
        state_list = state.split(",") if state else None
        college_type_list = college_type.split(",") if college_type else None
        size_category_list = size_category.split(",") if size_category else None

        # Build search filters
        filters = CollegeSearchFilters(
            page=page,
            limit=limit,
            search_query=search_query,
            state=state_list,
            city=city,
            region=region,
            college_type=college_type_list,
            size_category=size_category_list,
            carnegie_classification=carnegie_classification,
            hbcu_only=hbcu_only,
            hsi_only=hsi_only,
            women_only=women_only,
            religious_only=religious_only,
            min_enrollment=min_enrollment,
            max_enrollment=max_enrollment,
            min_acceptance_rate=min_acceptance_rate,
            max_acceptance_rate=max_acceptance_rate,
            student_gpa=student_gpa,
            student_sat_score=student_sat_score,
            student_act_score=student_act_score,
            max_tuition=max_tuition,
            max_total_cost=max_total_cost,
            in_state_student=in_state_student,
            major_interest=major_interest,
            urban_setting=urban_setting,
            requires_on_campus_housing=requires_on_campus_housing,
            ncaa_division=ncaa_division,
            test_optional_only=test_optional_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        service = CollegeService(db)
        colleges, total_count, search_metadata = service.search_colleges(filters)

        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit

        return CollegeSearchResponse(
            colleges=[CollegeResponse.model_validate(c) for c in colleges],
            pagination={
                "current_page": page,
                "total_pages": total_pages,
                "total_results": total_count,
                "items_per_page": limit,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
            search_metadata=search_metadata,
        )

    except Exception as e:
        logger.error(f"College search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/search/insights", response_model=CollegeInsightsResponse)
async def get_search_insights(
    # Use same parameters as search endpoint but only return insights
    search_query: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    college_type: Optional[str] = Query(None),
    max_acceptance_rate: Optional[float] = Query(None, ge=0, le=100),
    max_tuition: Optional[int] = Query(None, ge=0),
    student_gpa: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    """
    Get insights about search criteria without returning full results.
    Useful for helping users refine their search.
    """
    try:
        # Build simplified filters for insights
        filters = CollegeSearchFilters(
            search_query=search_query,
            state=state.split(",") if state else None,
            college_type=college_type.split(",") if college_type else None,
            max_acceptance_rate=max_acceptance_rate,
            max_tuition=max_tuition,
            student_gpa=student_gpa,
            limit=1,  # We only need count, not results
        )

        service = CollegeService(db)
        insights = service.get_search_insights(filters)

        return CollegeInsightsResponse(**insights)

    except Exception as e:
        logger.error(f"Search insights failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insights failed: {str(e)}",
        )


# ===========================
# INDIVIDUAL COLLEGE ENDPOINTS
# ===========================


@router.get("/{college_id}", response_model=CollegeResponse)
async def get_college(college_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific college"""
    try:
        service = CollegeService(db)
        college = service.get_college_by_id(college_id)

        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="College not found"
            )

        return CollegeResponse.model_validate(college)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get college failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get college: {str(e)}",
        )


@router.get("/{college_id}/similar", response_model=List[CollegeResponse])
async def get_similar_colleges(
    college_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of similar colleges"),
    db: Session = Depends(get_db),
):
    """Find colleges similar to the specified college"""
    try:
        service = CollegeService(db)
        similar_colleges = service.find_similar_colleges(college_id, limit)

        return [CollegeResponse.model_validate(c) for c in similar_colleges]

    except Exception as e:
        logger.error(f"Similar colleges search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similar colleges search failed: {str(e)}",
        )


# ===========================
# COLLEGE MATCHING
# ===========================


@router.post("/match", response_model=List[CollegeMatchResponse])
async def find_college_matches(
    match_request: CollegeMatchRequest, db: Session = Depends(get_db)
):
    """
    Find colleges that match a student's profile and preferences.
    Returns colleges with match scores and explanations.
    """
    try:
        service = CollegeService(db)

        # Convert match request to search filters
        filters = CollegeSearchFilters(
            limit=match_request.max_results,
            student_gpa=match_request.gpa,
            student_sat_score=match_request.sat_score,
            student_act_score=match_request.act_score,
            major_interest=match_request.intended_major,
            state=match_request.preferred_states,
            max_total_cost=match_request.max_budget,
            size_category=match_request.preferred_size,
            hbcu_only=match_request.prefer_hbcu,
            women_only=match_request.prefer_women_college,
            religious_only=match_request.prefer_religious,
        )

        # Get potential matches
        colleges, _, _ = service.search_colleges(filters)

        # Calculate match scores and build response
        matches = []
        student_profile = match_request.model_dump(exclude_none=True)

        for college in colleges:
            match_score = service.get_match_score(college, student_profile)

            if match_score >= match_request.match_threshold:
                # Generate match reasons
                match_reasons = []

                if match_request.intended_major and college.all_majors_offered:
                    if match_request.intended_major in college.all_majors_offered:
                        match_reasons.append(
                            f"Offers {match_request.intended_major} program"
                        )

                if match_request.gpa and college.acceptance_rate:
                    if college.acceptance_rate >= 50:
                        match_reasons.append("Good academic fit for your GPA")
                    elif college.acceptance_rate >= 25 and match_request.gpa >= 3.5:
                        match_reasons.append("Competitive but achievable with your GPA")

                if match_request.max_budget:
                    relevant_cost = (
                        college.total_cost_in_state
                        if match_request.preferred_states
                        and college.state in match_request.preferred_states
                        else college.total_cost_out_state
                    )
                    if relevant_cost and relevant_cost <= match_request.max_budget:
                        match_reasons.append("Within your budget")

                if (
                    match_request.preferred_states
                    and college.state in match_request.preferred_states
                ):
                    match_reasons.append("In your preferred state")

                # Calculate category scores
                academic_score, _ = service._calculate_academic_match(
                    college, student_profile
                )
                financial_score, _ = service._calculate_financial_match(
                    college, student_profile
                )
                location_score, _ = service._calculate_location_match(
                    college, student_profile
                )
                culture_score, _ = service._calculate_culture_match(
                    college, student_profile
                )

                matches.append(
                    CollegeMatchResponse(
                        college=CollegeResponse.model_validate(college),
                        match_score=match_score,
                        match_reasons=match_reasons,
                        category_scores={
                            "academic": academic_score,
                            "financial": financial_score,
                            "location": location_score,
                            "culture": culture_score,
                        },
                    )
                )

        # Sort by match score
        matches.sort(key=lambda x: x.match_score, reverse=True)

        return matches

    except Exception as e:
        logger.error(f"College matching failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"College matching failed: {str(e)}",
        )


# ===========================
# USER FAVORITES
# ===========================


@router.post("/favorites", response_model=CollegeFavoriteResponse)
async def add_to_favorites(
    favorite_data: CollegeFavoriteCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a college to user's favorites"""
    try:
        service = CollegeService(db)

        # Verify college exists
        college = service.get_college_by_id(favorite_data.college_id)
        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="College not found"
            )

        favorite = service.add_to_favorites(
            user_id=current_user["id"],
            college_id=favorite_data.college_id,
            notes=favorite_data.notes,
        )

        # Build response with college data
        response_data = {
            "id": favorite.id,
            "user_id": favorite.user_id,
            "college_id": favorite.college_id,
            "notes": favorite.notes,
            "created_at": favorite.created_at,
            "college": CollegeResponse.model_validate(college),
        }

        return CollegeFavoriteResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to favorites failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to favorites: {str(e)}",
        )


@router.get("/favorites", response_model=List[CollegeFavoriteResponse])
async def get_user_favorites(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get user's favorite colleges"""
    try:
        service = CollegeService(db)
        favorites = service.get_user_favorites(current_user["id"])

        # Get favorite records with details
        from app.models.college import CollegeFavorite

        favorite_records = (
            db.query(CollegeFavorite)
            .filter(CollegeFavorite.user_id == current_user["id"])
            .all()
        )

        response = []
        for favorite_record in favorite_records:
            college = service.get_college_by_id(favorite_record.college_id)
            if college:
                response.append(
                    CollegeFavoriteResponse(
                        id=favorite_record.id,
                        user_id=favorite_record.user_id,
                        college_id=favorite_record.college_id,
                        notes=favorite_record.notes,
                        created_at=favorite_record.created_at,
                        college=CollegeResponse.model_validate(college),
                    )
                )

        return response

    except Exception as e:
        logger.error(f"Get favorites failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get favorites: {str(e)}",
        )


@router.delete("/favorites/{college_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    college_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a college from user's favorites"""
    try:
        service = CollegeService(db)
        success = service.remove_from_favorites(current_user["id"], college_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove from favorites failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove from favorites: {str(e)}",
        )


# ===========================
# SAVED SEARCHES
# ===========================


@router.post("/saved-searches", response_model=CollegeSavedSearchResponse)
async def save_search(
    search_data: CollegeSavedSearchCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a college search for later use"""
    try:
        service = CollegeService(db)
        saved_search = service.save_search(
            user_id=current_user["id"],
            search_name=search_data.search_name,
            search_criteria=search_data.search_criteria,
        )

        return CollegeSavedSearchResponse.model_validate(saved_search)

    except Exception as e:
        logger.error(f"Save search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save search: {str(e)}",
        )


@router.get("/saved-searches", response_model=List[CollegeSavedSearchResponse])
async def get_saved_searches(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get user's saved college searches"""
    try:
        service = CollegeService(db)
        saved_searches = service.get_user_saved_searches(current_user["id"])

        return [
            CollegeSavedSearchResponse.model_validate(search)
            for search in saved_searches
        ]

    except Exception as e:
        logger.error(f"Get saved searches failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get saved searches: {str(e)}",
        )


@router.post("/saved-searches/{search_id}/run", response_model=CollegeSearchResponse)
async def run_saved_search(
    search_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run a previously saved search"""
    try:
        # Get the saved search
        from app.models.college import CollegeSavedSearch

        saved_search = (
            db.query(CollegeSavedSearch)
            .filter(
                CollegeSavedSearch.id == search_id,
                CollegeSavedSearch.user_id == current_user["id"],
            )
            .first()
        )

        if not saved_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found"
            )

        # Convert saved criteria to search filters
        criteria = saved_search.search_criteria
        criteria.update({"page": page, "limit": limit})

        filters = CollegeSearchFilters(**criteria)

        service = CollegeService(db)
        colleges, total_count, search_metadata = service.search_colleges(filters)

        # Update last run time and results count
        saved_search.last_run_at = func.now()
        saved_search.results_count = total_count
        db.commit()

        # Build response
        total_pages = (total_count + limit - 1) // limit

        return CollegeSearchResponse(
            colleges=[CollegeResponse.model_validate(c) for c in colleges],
            pagination={
                "current_page": page,
                "total_pages": total_pages,
                "total_results": total_count,
                "items_per_page": limit,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
            search_metadata=search_metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run saved search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run saved search: {str(e)}",
        )


# ===========================
# COLLEGE COMPARISON
# ===========================


@router.post("/compare", response_model=Dict[str, Any])
async def compare_colleges(
    comparison_request: CollegeComparisonRequest, db: Session = Depends(get_db)
):
    """Compare multiple colleges side by side"""
    try:
        service = CollegeService(db)

        # Get all colleges to compare
        colleges = []
        for college_id in comparison_request.college_ids:
            college = service.get_college_by_id(college_id)
            if not college:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"College with ID {college_id} not found",
                )
            colleges.append(college)

        # Build comparison data
        comparison = {
            "colleges": [CollegeResponse.model_validate(c) for c in colleges],
            "comparison_data": {},
        }

        # Add comparison categories
        if "academics" in comparison_request.comparison_categories:
            comparison["comparison_data"]["academics"] = {
                "acceptance_rate": [c.acceptance_rate for c in colleges],
                "sat_ranges": [c.sat_range_string for c in colleges],
                "act_ranges": [c.act_range_string for c in colleges],
                "graduation_rate_6_year": [c.graduation_rate_6_year for c in colleges],
                "student_faculty_ratio": [c.student_faculty_ratio for c in colleges],
            }

        if "financial" in comparison_request.comparison_categories:
            comparison["comparison_data"]["financial"] = {
                "tuition_in_state": [c.tuition_in_state for c in colleges],
                "tuition_out_state": [c.tuition_out_state for c in colleges],
                "total_cost_in_state": [c.total_cost_in_state for c in colleges],
                "total_cost_out_state": [c.total_cost_out_state for c in colleges],
                "percent_receiving_aid": [c.percent_receiving_aid for c in colleges],
                "average_aid_amount": [c.average_aid_amount for c in colleges],
            }

        if "admissions" in comparison_request.comparison_categories:
            comparison["comparison_data"]["admissions"] = {
                "acceptance_rate": [c.acceptance_rate for c in colleges],
                "yield_rate": [c.yield_rate for c in colleges],
                "requires_essay": [c.requires_essay for c in colleges],
                "is_test_optional": [c.is_test_optional for c in colleges],
                "requires_interview": [c.requires_interview for c in colleges],
            }

        if "campus_life" in comparison_request.comparison_categories:
            comparison["comparison_data"]["campus_life"] = {
                "total_enrollment": [c.total_enrollment for c in colleges],
                "campus_setting": [
                    c.campus_setting.value if c.campus_setting else None
                    for c in colleges
                ],
                "percent_students_on_campus": [
                    c.percent_students_on_campus for c in colleges
                ],
                "ncaa_division": [c.ncaa_division for c in colleges],
                "housing_required": [c.housing_required for c in colleges],
            }

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"College comparison failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"College comparison failed: {str(e)}",
        )


# ===========================
# ADMIN ENDPOINTS (for data management)
# ===========================


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CollegeResponse)
async def create_college(
    college_data: CollegeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new college (Admin only)"""
    try:
        service = CollegeService(db)
        college = service.create_college(college_data)
        return CollegeResponse.model_validate(college)

    except Exception as e:
        logger.error(f"Create college failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create college: {str(e)}",
        )


@router.put("/{college_id}", response_model=CollegeResponse)
async def update_college(
    college_id: int,
    college_data: CollegeUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update college information (Admin only)"""
    try:
        service = CollegeService(db)
        college = service.get_college_by_id(college_id)

        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="College not found"
            )

        # Update fields
        update_data = college_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(college, field):
                setattr(college, field, value)

        db.commit()
        db.refresh(college)

        return CollegeResponse.model_validate(college)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update college failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update college: {str(e)}",
        )


@router.post("/bulk/create", response_model=Dict[str, Any])
async def bulk_create_colleges(
    bulk_data: BulkCollegeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk create colleges from IPEDS data (Admin only)"""
    try:
        service = CollegeService(db)
        created_colleges = []
        errors = []

        for i, college_data in enumerate(bulk_data.colleges):
            try:
                college = service.create_college(college_data)
                created_colleges.append(college)
            except Exception as e:
                error_msg = (
                    f"Error creating college {i+1} ({college_data.name}): {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)

        return {
            "message": "Bulk creation completed",
            "created_count": len(created_colleges),
            "error_count": len(errors),
            "created_colleges": [
                CollegeResponse.model_validate(c) for c in created_colleges
            ],
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Bulk create colleges failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk creation failed: {str(e)}",
        )


# ===========================
# ANALYTICS ENDPOINTS
# ===========================


@router.get("/analytics/overview", response_model=Dict[str, Any])
async def get_college_analytics(db: Session = Depends(get_db)):
    """Get overall college database analytics"""
    try:
        from app.models.college import College

        # Basic counts
        total_colleges = db.query(College).filter(College.is_active == True).count()

        # By type
        type_counts = (
            db.query(College.college_type, func.count(College.id))
            .filter(College.is_active == True)
            .group_by(College.college_type)
            .all()
        )

        # By state (top 10)
        state_counts = (
            db.query(College.state, func.count(College.id))
            .filter(College.is_active == True)
            .group_by(College.state)
            .order_by(func.count(College.id).desc())
            .limit(10)
            .all()
        )

        # Acceptance rate distribution
        acceptance_stats = (
            db.query(
                func.min(College.acceptance_rate),
                func.max(College.acceptance_rate),
                func.avg(College.acceptance_rate),
            )
            .filter(College.is_active == True, College.acceptance_rate.isnot(None))
            .first()
        )

        return {
            "total_colleges": total_colleges,
            "by_type": {str(t[0]): t[1] for t in type_counts},
            "top_states": {t[0]: t[1] for t in state_counts},
            "acceptance_rate_stats": (
                {
                    "min": float(acceptance_stats[0]) if acceptance_stats[0] else None,
                    "max": float(acceptance_stats[1]) if acceptance_stats[1] else None,
                    "avg": float(acceptance_stats[2]) if acceptance_stats[2] else None,
                }
                if acceptance_stats
                else None
            ),
        }

    except Exception as e:
        logger.error(f"Analytics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics failed: {str(e)}",
        )
