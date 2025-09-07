# app/api/v1/institutions.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError
from typing import Optional, List

from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import (
    InstitutionResponse,
    InstitutionList,
    InstitutionSearch,
)
from app.services.institution import InstitutionService

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


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
                # Computed properties
                "full_address": institution.full_address,
                "display_name": institution.display_name,
                "is_public": institution.is_public,
                "is_private": institution.is_private,
                "display_image_url": institution.display_image_url,
                "has_high_quality_image": institution.has_high_quality_image,
                "has_good_image": institution.has_good_image,
                "image_needs_attention": institution.image_needs_attention,
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


@router.get("/featured", response_model=List[InstitutionResponse])
async def get_featured_institutions(
    limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
):
    """Get featured institutions with best images for homepage"""
    try:
        service = InstitutionService(db)
        institutions = service.get_featured_institutions(limit)
        return institutions
    except Exception as e:
        logger.error(f"Error getting featured institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get featured institutions: {str(e)}",
        )
