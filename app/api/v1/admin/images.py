# app/api/v1/admin/images.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.services.image_extractor import MagicScholarImageExtractor
from app.services.institution import InstitutionService
from app.models.institution import Institution, ImageExtractionStatus

logger = logging.getLogger(__name__)

router = APIRouter()


# Response schemas
from pydantic import BaseModel
from typing import Dict, Any


class ImageProcessingResult(BaseModel):
    institution_id: int
    name: str
    status: str
    cdn_urls: Dict[str, str] = {}
    quality_score: Optional[int] = None
    error: Optional[str] = None


class BatchProcessingResponse(BaseModel):
    batch_id: str
    total_processed: int
    successful: int
    failed: int
    no_images: int
    no_website: int
    stats: Dict[str, Any]
    results: List[ImageProcessingResult]


class ProcessingStatsResponse(BaseModel):
    total_institutions: int
    with_images: int
    high_quality_images: int
    good_quality_images: int
    pending_processing: int
    failed_processing: int
    success_rate: str
    high_quality_rate: str


class InstitutionImageStatus(BaseModel):
    ipeds_id: int
    name: str
    primary_image_url: Optional[str]
    primary_image_quality_score: Optional[int]
    logo_image_url: Optional[str]
    image_extraction_status: str
    image_extraction_date: Optional[datetime]
    website_url: Optional[str]


def run_image_extraction_batch(institution_ids: List[int], db: Session):
    """Background task to run image extraction"""
    try:
        extractor = MagicScholarImageExtractor(db)
        result = extractor.process_institutions_batch(institution_ids=institution_ids)
        logger.info(
            f"Batch processing completed: {result['successful']} successful, {result['failed']} failed"
        )
        return result
    except Exception as e:
        logger.error(f"Background batch processing failed: {e}")
        raise


@router.post("/extract-batch", response_model=BatchProcessingResponse)
async def extract_images_batch(
    background_tasks: BackgroundTasks,
    institution_ids: Optional[List[int]] = None,
    limit: Optional[int] = Query(
        None, description="Limit number of institutions to process"
    ),
    run_in_background: bool = Query(False, description="Run extraction in background"),
    db: Session = Depends(get_db),
):
    """
    Extract and upload images for a batch of institutions
    This endpoint scrapes university websites, processes images, and uploads to Digital Ocean Spaces
    """
    try:
        batch_id = f"batch_{int(datetime.now().timestamp())}"

        # Validate institution IDs if provided
        if institution_ids:
            existing_count = (
                db.query(Institution)
                .filter(Institution.ipeds_id.in_(institution_ids))
                .count()
            )
            if existing_count != len(institution_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Some institution IDs not found. Found {existing_count} of {len(institution_ids)}",
                )

        # Create extractor instance
        extractor = MagicScholarImageExtractor(db)

        if run_in_background:
            # Run in background for large batches
            background_tasks.add_task(
                run_image_extraction_batch, institution_ids or [], db
            )

            return BatchProcessingResponse(
                batch_id=batch_id,
                total_processed=0,
                successful=0,
                failed=0,
                no_images=0,
                no_website=0,
                stats={"message": "Processing started in background"},
                results=[],
            )
        else:
            # Run synchronously for smaller batches
            result = extractor.process_institutions_batch(
                institution_ids=institution_ids, limit=limit
            )

            # Convert results to response format
            processed_results = []
            for r in result["results"]:
                processed_results.append(
                    ImageProcessingResult(
                        institution_id=r["institution_id"],
                        name=r["name"],
                        status=r["status"],
                        cdn_urls=r.get("cdn_urls", {}),
                        quality_score=r.get("best_image", {}).get("quality_score"),
                        error=r.get("error"),
                    )
                )

            return BatchProcessingResponse(
                batch_id=batch_id,
                total_processed=result["total_processed"],
                successful=result["successful"],
                failed=result["failed"],
                no_images=result["no_images"],
                no_website=result["no_website"],
                stats=result["stats"],
                results=processed_results,
            )

    except Exception as e:
        logger.error(f"Error in extract_images_batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch: {str(e)}",
        )


@router.get("/stats", response_model=ProcessingStatsResponse)
async def get_processing_stats(db: Session = Depends(get_db)):
    """Get current image processing statistics"""
    try:
        extractor = MagicScholarImageExtractor(db)
        stats = extractor.get_processing_stats()

        return ProcessingStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting processing stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing stats: {str(e)}",
        )


@router.get("/status", response_model=List[InstitutionImageStatus])
async def get_institutions_image_status(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    status_filter: Optional[str] = Query(
        None, description="Filter by extraction status"
    ),
    min_quality: Optional[int] = Query(
        None, ge=0, le=100, description="Minimum quality score"
    ),
    has_image: Optional[bool] = Query(
        None, description="Filter by whether institution has image"
    ),
    db: Session = Depends(get_db),
):
    """Get institutions with their image processing status"""
    try:
        # Build query
        query = db.query(Institution)

        # Apply filters
        if status_filter:
            try:
                status_enum = ImageExtractionStatus(status_filter)
                query = query.filter(Institution.image_extraction_status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}",
                )

        if min_quality is not None:
            query = query.filter(Institution.primary_image_quality_score >= min_quality)

        if has_image is not None:
            if has_image:
                query = query.filter(Institution.primary_image_url.isnot(None))
            else:
                query = query.filter(Institution.primary_image_url.is_(None))

        # Apply pagination
        offset = (page - 1) * per_page
        institutions = query.offset(offset).limit(per_page).all()

        # Convert to response format
        result = []
        for institution in institutions:
            result.append(
                InstitutionImageStatus(
                    ipeds_id=institution.ipeds_id,
                    name=institution.name,
                    primary_image_url=institution.primary_image_url,
                    primary_image_quality_score=institution.primary_image_quality_score,
                    logo_image_url=institution.logo_image_url,
                    image_extraction_status=(
                        institution.image_extraction_status.value
                        if institution.image_extraction_status
                        else "pending"
                    ),
                    image_extraction_date=institution.image_extraction_date,
                    website_url=institution.website_url,
                )
            )

        return result

    except Exception as e:
        logger.error(f"Error getting image status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get image status: {str(e)}",
        )


@router.post("/extract-single/{institution_id}")
async def extract_single_institution_images(
    institution_id: int, db: Session = Depends(get_db)
):
    """Extract images for a single institution by IPEDS ID"""
    try:
        # Find institution
        institution = (
            db.query(Institution).filter(Institution.ipeds_id == institution_id).first()
        )

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with IPEDS ID {institution_id} not found",
            )

        # Create extractor and process
        extractor = MagicScholarImageExtractor(db)
        result = extractor.process_institution(institution)

        return ImageProcessingResult(
            institution_id=result["institution_id"],
            name=result["name"],
            status=result["status"],
            cdn_urls=result.get("cdn_urls", {}),
            quality_score=result.get("best_image", {}).get("quality_score"),
            error=result.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting images for institution {institution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract images: {str(e)}",
        )


@router.post("/retry-failed")
async def retry_failed_extractions(
    background_tasks: BackgroundTasks,
    limit: Optional[int] = Query(
        None, description="Limit number of institutions to retry"
    ),
    run_in_background: bool = Query(True, description="Run retry in background"),
    db: Session = Depends(get_db),
):
    """Retry image extraction for institutions that previously failed"""
    try:
        # Get failed institutions
        failed_institutions = db.query(Institution).filter(
            Institution.image_extraction_status == ImageExtractionStatus.FAILED
        )

        if limit:
            failed_institutions = failed_institutions.limit(limit)

        failed_ids = [inst.ipeds_id for inst in failed_institutions.all()]

        if not failed_ids:
            return {"message": "No failed institutions to retry", "count": 0}

        if run_in_background:
            background_tasks.add_task(run_image_extraction_batch, failed_ids, db)
            return {
                "message": f"Retry started in background for {len(failed_ids)} institutions",
                "count": len(failed_ids),
            }
        else:
            extractor = MagicScholarImageExtractor(db)
            result = extractor.process_institutions_batch(institution_ids=failed_ids)
            return {
                "message": f"Retry completed",
                "count": len(failed_ids),
                "successful": result["successful"],
                "failed": result["failed"],
            }

    except Exception as e:
        logger.error(f"Error retrying failed extractions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry extractions: {str(e)}",
        )


@router.delete("/clear-processing-status")
async def clear_processing_status(
    reset_to_pending: bool = Query(
        True, description="Reset status to pending instead of clearing"
    ),
    db: Session = Depends(get_db),
):
    """Clear or reset processing status for institutions currently marked as processing"""
    try:
        processing_institutions = db.query(Institution).filter(
            Institution.image_extraction_status == ImageExtractionStatus.PROCESSING
        )

        count = processing_institutions.count()

        if reset_to_pending:
            processing_institutions.update(
                {Institution.image_extraction_status: ImageExtractionStatus.PENDING}
            )
        else:
            processing_institutions.update(
                {
                    Institution.image_extraction_status: None,
                    Institution.image_extraction_date: None,
                }
            )

        db.commit()

        action = "reset to pending" if reset_to_pending else "cleared"
        return {
            "message": f"Processing status {action} for {count} institutions",
            "count": count,
        }

    except Exception as e:
        logger.error(f"Error clearing processing status: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear processing status: {str(e)}",
        )


# Legacy endpoints for backwards compatibility
@router.post("/upload-batch")
async def upload_batch_legacy():
    """Legacy endpoint - redirects to extract-batch"""
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="This endpoint has been moved to /extract-batch",
    )
