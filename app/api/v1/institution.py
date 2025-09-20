# app/api/v1/institution.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError
from typing import Optional, List
from sqlalchemy import or_

from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import (
    InstitutionResponse,
    InstitutionList,
    InstitutionSearch,
    CustomerRankUpdate,
)
from app.services.institution import InstitutionService

import logging

logger = logging.getLogger(__name__)

print("=== LOADING INSTITUTION ROUTER ===")
router = APIRouter()
print("Router created successfully")


@router.get("/featured", response_model=List[InstitutionResponse])
async def get_featured_institutions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get featured institutions with best images for homepage with pagination support"""
    try:
        service = InstitutionService(db)
        institutions = service.get_featured_institutions(limit, offset)
        return institutions
    except Exception as e:
        logger.error(f"Error getting featured institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get featured institutions: {str(e)}",
        )


@router.get("/search", response_model=InstitutionList)
async def search_institutions(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search institutions by name, city, or state with pagination"""
    try:
        service = InstitutionService(db)

        # FIXED: Create search params that actually search across name, city, state
        # We'll search the query against all these fields
        search_params = InstitutionSearch(
            query=query  # Pass the raw query to be handled by the service
        )
        institutions, total = service.search_institutions(search_params, page, per_page)

        return InstitutionList(
            institutions=institutions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page,
        )
    except Exception as e:
        logger.error(f"Error searching institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search institutions: {str(e)}",
        )


@router.get("/by-priority", response_model=List[InstitutionResponse])
async def get_institutions_by_priority(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get institutions ordered by customer priority (for admin dashboard)"""
    try:
        service = InstitutionService(db)
        institutions = service.get_institutions_by_customer_priority(limit, offset)
        return [InstitutionResponse.model_validate(inst) for inst in institutions]

    except Exception as e:
        logger.error(f"Error getting institutions by priority: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institutions by priority: {str(e)}",
        )


@router.get("/", response_model=InstitutionList)
async def list_institutions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    min_image_quality: Optional[int] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Get institutions ordered by image quality (best first)"""
    try:
        service = InstitutionService(db)

        search_params = InstitutionSearch(min_image_quality=min_image_quality)
        institutions, total = service.search_institutions(search_params, page, per_page)

        return InstitutionList(
            institutions=institutions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page,
        )
    except Exception as e:
        logger.error(f"Error listing institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list institutions: {str(e)}",
        )


@router.post("/bulk-update-ranks")
async def bulk_update_customer_ranks(
    updates: List[dict],  # [{"institution_id": 1, "customer_rank": 95}, ...]
    db: Session = Depends(get_db),
):
    """Bulk update customer ranks for multiple institutions"""
    try:
        service = InstitutionService(db)
        updated_count = 0
        failed_count = 0
        errors = []

        for update in updates:
            try:
                institution_id = update.get("institution_id")
                customer_rank = update.get("customer_rank")

                if institution_id is None or customer_rank is None:
                    failed_count += 1
                    errors.append(
                        f"Missing institution_id or customer_rank in update: {update}"
                    )
                    continue

                result = service.update_customer_rank(institution_id, customer_rank)
                if result:
                    updated_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Institution {institution_id} not found")

            except Exception as e:
                failed_count += 1
                errors.append(f"Error updating institution {institution_id}: {str(e)}")

        return {
            "message": f"Bulk update completed: {updated_count} successful, {failed_count} failed",
            "updated_count": updated_count,
            "failed_count": failed_count,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Error in bulk customer rank update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update customer ranks: {str(e)}",
        )


@router.put("/{institution_id}/customer-rank", response_model=InstitutionResponse)
async def update_customer_rank(
    institution_id: int, rank_update: CustomerRankUpdate, db: Session = Depends(get_db)
):
    """Update customer ranking for an institution (for advertising tier changes)"""
    try:
        service = InstitutionService(db)
        institution = service.update_customer_rank(
            institution_id, rank_update.customer_rank
        )

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with ID {institution_id} not found",
            )

        return InstitutionResponse.model_validate(institution)

    except Exception as e:
        logger.error(
            f"Error updating customer rank for institution {institution_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update customer rank: {str(e)}",
        )


# MOVED TO THE END: This route must come last because it catches all /{institution_id}
@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution_by_id(institution_id: int, db: Session = Depends(get_db)):
    """Get institution by ID with complete image information"""
    try:
        institution = (
            db.query(Institution).filter(Institution.id == institution_id).first()
        )

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with ID {institution_id} not found",
            )

        # Add logging to debug the institution data
        logger.info(f"Institution data for ID {institution_id}:")
        logger.info(f"  Name: {institution.name}")
        logger.info(f"  Phone: '{institution.phone}' (type: {type(institution.phone)})")
        logger.info(f"  Primary Image URL: {institution.primary_image_url}")
        logger.info(f"  Image Quality Score: {institution.primary_image_quality_score}")
        logger.info(f"  Logo URL: {institution.logo_image_url}")
        logger.info(f"  Image Status: {institution.image_extraction_status}")
        logger.info(f"  Display Image URL: {institution.display_image_url}")

        # Try to validate and catch specific validation errors
        try:
            # Create response data with computed properties
            response_data = {
                # Basic institution fields
                "id": institution.id,
                "ipeds_id": institution.ipeds_id,
                "name": institution.name,
                "address": institution.address,
                "city": institution.city,
                "state": institution.state,
                "zip_code": institution.zip_code,
                "region": institution.region,
                "website": institution.website,
                "phone": institution.phone,
                "president_name": institution.president_name,
                "president_title": institution.president_title,
                "control_type": institution.control_type,
                "size_category": institution.size_category,
                # Image fields
                "primary_image_url": institution.primary_image_url,
                "primary_image_quality_score": institution.primary_image_quality_score,
                "logo_image_url": institution.logo_image_url,
                "image_extraction_status": institution.image_extraction_status,
                "image_extraction_date": institution.image_extraction_date,
                # Note: computed properties are handled by the schema automatically
            }

            response = InstitutionResponse.model_validate(response_data)
            logger.info("Validation successful")
            return response

        except ValidationError as ve:
            logger.error(f"Validation error for institution {institution_id}: {ve}")
            logger.error(f"Validation error details: {ve.errors()}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {ve.errors()}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting institution {institution_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institution: {str(e)}",
        )


print(f"=== INSTITUTION ROUTER LOADED: {len(router.routes)} routes ===")
for route in router.routes:
    print(f"  {list(route.methods)}: {route.path}")
print("=== END INSTITUTION ROUTER ===")
