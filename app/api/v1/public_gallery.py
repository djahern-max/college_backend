"""
Public gallery endpoints for MagicScholar.
Displays gallery images from the unified database (managed by Abacadaba).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.core.database import get_db
from app.models.entity_image import EntityImage
from app.models.institution import Institution
from app.schemas.entity_image import EntityImageResponse

router = APIRouter(tags=["gallery"])


@router.get(
    "/institutions/{institution_id}/images", response_model=List[EntityImageResponse]
)
def get_institution_gallery(institution_id: int, db: Session = Depends(get_db)):
    """
    Get all gallery images for an institution.
    PUBLIC endpoint - no authentication required.
    """
    images = (
        db.query(EntityImage)
        .filter(
            and_(
                EntityImage.entity_type == "institution",
                EntityImage.entity_id == institution_id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
        .all()
    )

    return images


@router.get(
    "/institutions/{institution_id}/featured",
    response_model=Optional[EntityImageResponse],
)
def get_institution_featured_image(institution_id: int, db: Session = Depends(get_db)):
    """
    Get the featured/primary image for an institution.
    PUBLIC endpoint.
    """
    image = (
        db.query(EntityImage)
        .filter(
            and_(
                EntityImage.entity_type == "institution",
                EntityImage.entity_id == institution_id,
                EntityImage.is_featured == True,
            )
        )
        .first()
    )

    return image


@router.get(
    "/institutions/ipeds/{ipeds_id}/images", response_model=List[EntityImageResponse]
)
def get_institution_gallery_by_ipeds(ipeds_id: int, db: Session = Depends(get_db)):
    """
    Get gallery images for an institution by IPEDS ID.
    More convenient since MagicScholar uses IPEDS IDs.
    """
    # First get the institution
    institution = db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    # Then get its gallery
    images = (
        db.query(EntityImage)
        .filter(
            and_(
                EntityImage.entity_type == "institution",
                EntityImage.entity_id == institution.id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
        .all()
    )

    return images


@router.get(
    "/institutions/ipeds/{ipeds_id}/featured",
    response_model=Optional[EntityImageResponse],
)
def get_institution_featured_image_by_ipeds(
    ipeds_id: int, db: Session = Depends(get_db)
):
    """
    Get the featured image for an institution by IPEDS ID.
    """
    # First get the institution
    institution = db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    # Then get its featured image
    image = (
        db.query(EntityImage)
        .filter(
            and_(
                EntityImage.entity_type == "institution",
                EntityImage.entity_id == institution.id,
                EntityImage.is_featured == True,
            )
        )
        .first()
    )

    return image


@router.get(
    "/scholarships/{scholarship_id}/images", response_model=List[EntityImageResponse]
)
def get_scholarship_gallery(scholarship_id: int, db: Session = Depends(get_db)):
    """
    Get all gallery images for a scholarship.
    PUBLIC endpoint.
    """
    images = (
        db.query(EntityImage)
        .filter(
            and_(
                EntityImage.entity_type == "scholarship",
                EntityImage.entity_id == scholarship_id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
        .all()
    )

    return images


@router.get(
    "/scholarships/{scholarship_id}/featured",
    response_model=Optional[EntityImageResponse],
)
def get_scholarship_featured_image(scholarship_id: int, db: Session = Depends(get_db)):
    """
    Get the featured image for a scholarship.
    PUBLIC endpoint.
    """
    image = (
        db.query(EntityImage)
        .filter(
            and_(
                EntityImage.entity_type == "scholarship",
                EntityImage.entity_id == scholarship_id,
                EntityImage.is_featured == True,
            )
        )
        .first()
    )

    return image
