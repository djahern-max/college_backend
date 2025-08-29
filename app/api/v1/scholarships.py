# app/api/v1/scholarships.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services.scholarship_extractor import (
    ScholarshipExtractor,
    ScholarshipEnrichmentService,
)
from pydantic import BaseModel, HttpUrl

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

import logging

logger = logging.getLogger(__name__)

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


# Add these schemas at the top of the file
class ScholarshipExtractionRequest(BaseModel):
    """Request to extract scholarship data from a URL"""

    url: HttpUrl
    auto_create: bool = False  # Whether to automatically create the scholarship

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.fastweb.com/college-scholarships/scholarships/123456/stem-excellence-award",
                "auto_create": False,
            }
        }


class ScholarshipExtractionResponse(BaseModel):
    """Response from scholarship extraction"""

    success: bool
    extraction_confidence: int
    extracted_data: dict
    suggested_scholarship: Optional[dict] = None
    created_scholarship_id: Optional[int] = None
    warnings: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "extraction_confidence": 85,
                "extracted_data": {
                    "title": "STEM Excellence Scholarship",
                    "organization": "Tech Future Foundation",
                    "amount_exact": 5000,
                    "min_gpa": 3.5,
                    "essay_required": True,
                },
                "suggested_scholarship": {
                    "scholarship_type": "stem",
                    "difficulty_level": "moderate",
                },
                "warnings": ["Could not extract application deadline"],
            }
        }


# Add these endpoints to the scholarships router


@router.post("/extract", response_model=ScholarshipExtractionResponse)
async def extract_scholarship_data(
    extraction_request: ScholarshipExtractionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Extract scholarship data from a URL using intelligent parsing.
    Optionally auto-create the scholarship if extraction confidence is high.
    """
    try:
        # Initialize services
        extractor = ScholarshipExtractor()
        enrichment_service = ScholarshipEnrichmentService()

        # Extract data from URL
        extracted_data = await extractor.extract_from_url(str(extraction_request.url))

        # Check if extraction was successful
        if extracted_data.get("error"):
            return ScholarshipExtractionResponse(
                success=False,
                extraction_confidence=0,
                extracted_data=extracted_data,
                warnings=[f"Extraction failed: {extracted_data['error']}"],
            )

        confidence = extracted_data.get("extraction_confidence", 0)
        warnings = []
        created_scholarship_id = None
        suggested_scholarship = None

        # Generate enriched scholarship data
        try:
            scholarship_create = await enrichment_service.enrich_scholarship_data(
                extracted_data
            )
            suggested_scholarship = scholarship_create.model_dump()
        except Exception as e:
            warnings.append(f"Failed to enrich data: {str(e)}")

        # Auto-create if requested and confidence is high enough
        if (
            extraction_request.auto_create
            and confidence >= 70
            and suggested_scholarship
            and extracted_data.get("title")
            and extracted_data.get("organization")
        ):

            try:
                service = ScholarshipService(db)
                scholarship = service.create_scholarship(
                    scholarship_create, created_by_user_id=current_user["id"]
                )
                created_scholarship_id = scholarship.id
            except Exception as e:
                warnings.append(f"Auto-creation failed: {str(e)}")

        # Add extraction quality warnings
        if confidence < 50:
            warnings.append("Low extraction confidence - manual review recommended")
        if not extracted_data.get("amount_exact"):
            warnings.append("Could not extract scholarship amount")
        if not extracted_data.get("deadline"):
            warnings.append("Could not extract application deadline")

        # Cleanup
        await extractor.close()
        await enrichment_service.close()

        return ScholarshipExtractionResponse(
            success=True,
            extraction_confidence=confidence,
            extracted_data=extracted_data,
            suggested_scholarship=suggested_scholarship,
            created_scholarship_id=created_scholarship_id,
            warnings=warnings,
        )

    except Exception as e:
        logger.error(f"Scholarship extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


@router.post("/extract/bulk", response_model=dict)
async def bulk_extract_scholarships(
    urls: List[HttpUrl],
    auto_create_threshold: int = Query(80, ge=0, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Extract scholarship data from multiple URLs in bulk.
    Auto-creates scholarships that meet the confidence threshold.
    """
    if len(urls) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 URLs per bulk extraction",
        )

    try:
        extractor = ScholarshipExtractor()
        enrichment_service = ScholarshipEnrichmentService()
        service = ScholarshipService(db)

        results = []
        created_count = 0

        for url in urls:
            try:
                # Extract data
                extracted_data = await extractor.extract_from_url(str(url))
                confidence = extracted_data.get("extraction_confidence", 0)

                result = {
                    "url": str(url),
                    "success": not extracted_data.get("error"),
                    "confidence": confidence,
                    "created": False,
                    "error": extracted_data.get("error"),
                }

                # Auto-create if confidence meets threshold
                if (
                    not extracted_data.get("error")
                    and confidence >= auto_create_threshold
                    and extracted_data.get("title")
                    and extracted_data.get("organization")
                ):

                    try:
                        scholarship_create = (
                            await enrichment_service.enrich_scholarship_data(
                                extracted_data
                            )
                        )
                        scholarship = service.create_scholarship(
                            scholarship_create, created_by_user_id=current_user["id"]
                        )
                        result["created"] = True
                        result["scholarship_id"] = scholarship.id
                        created_count += 1
                    except Exception as e:
                        result["creation_error"] = str(e)

                results.append(result)

            except Exception as e:
                results.append(
                    {
                        "url": str(url),
                        "success": False,
                        "error": str(e),
                        "created": False,
                    }
                )

        # Cleanup
        await extractor.close()
        await enrichment_service.close()

        return {
            "total_urls": len(urls),
            "successful_extractions": len([r for r in results if r["success"]]),
            "scholarships_created": created_count,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Bulk extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk extraction failed: {str(e)}",
        )


@router.post("/preview-extraction")
async def preview_extraction(
    url: HttpUrl,
    current_user: dict = Depends(get_current_user),
):
    """
    Preview what data would be extracted from a URL without creating a scholarship.
    Useful for testing the extraction before committing.
    """
    try:
        extractor = ScholarshipExtractor()
        extracted_data = await extractor.extract_from_url(str(url))
        await extractor.close()

        return {
            "url": str(url),
            "preview": extracted_data,
            "extraction_confidence": extracted_data.get("extraction_confidence", 0),
            "key_fields_found": {
                "title": bool(extracted_data.get("title")),
                "organization": bool(extracted_data.get("organization")),
                "description": bool(extracted_data.get("description")),
                "amount": bool(extracted_data.get("amount_exact")),
                "deadline": bool(extracted_data.get("deadline")),
                "requirements": any(
                    [
                        extracted_data.get("min_gpa"),
                        extracted_data.get("min_sat_score"),
                        extracted_data.get("min_act_score"),
                        extracted_data.get("essay_required"),
                    ]
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}",
        )


@router.get("/extraction/stats")
async def get_extraction_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get statistics about scholarship extractions and success rates.
    """
    try:
        # This would require tracking extraction attempts in the database
        # For now, return mock statistics
        return {
            "total_extractions": 0,
            "successful_extractions": 0,
            "average_confidence": 0.0,
            "auto_created_count": 0,
            "common_extraction_sources": [],
            "extraction_success_by_domain": {},
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get extraction statistics: {str(e)}",
        )
