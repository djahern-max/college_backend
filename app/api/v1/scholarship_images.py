# app/api/v1/admin/scholarship_images.py
"""
Admin API endpoints for scholarship image processing
Similar to enhanced_images.py but for scholarships
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.services.scholarship_image_extractor import ScholarshipImageExtractor
from app.models.scholarship import Scholarship
from app.models.institution import ImageExtractionStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Response schemas
from pydantic import BaseModel


class ScholarshipImageResult(BaseModel):
    scholarship_id: int
    title: str
    organization: str
    status: str
    cdn_urls: Dict[str, str] = {}
    quality_score: Optional[int] = None
    error: Optional[str] = None


class ScholarshipBatchProcessingResponse(BaseModel):
    batch_id: str
    total_processed: int
    successful: int
    failed: int
    no_website: int
    org_logos_found: int
    stats: Dict[str, Any]
    results: List[ScholarshipImageResult]


class ScholarshipImageStatus(BaseModel):
    id: int
    title: str
    organization: str
    website_url: Optional[str]
    primary_image_url: Optional[str]
    primary_image_quality_score: Optional[int]
    logo_image_url: Optional[str]
    image_extraction_status: str
    image_extraction_date: Optional[datetime]


class ScholarshipImageStats(BaseModel):
    total_scholarships: int
    with_websites: int
    with_images: int
    success_count: int
    pending_count: int
    failed_count: int
    high_quality_count: int
    good_quality_count: int
    success_rate: str
    high_quality_rate: str


def run_scholarship_extraction_background(
    scholarship_ids: Optional[List[int]],
    limit: Optional[int],
    force_reprocess: bool,
    db: Session,
):
    """Background task to run scholarship image extraction"""
    try:
        extractor = ScholarshipImageExtractor(db)
        result = extractor.process_scholarships_batch(
            scholarship_ids=scholarship_ids,
            limit=limit,
            force_reprocess=force_reprocess,
        )
        logger.info(
            f"Background scholarship processing completed: {result['successful']} successful, {result['failed']} failed"
        )
        return result
    except Exception as e:
        logger.error(f"Background scholarship processing failed: {e}")
        raise


@router.get("/stats", response_model=ScholarshipImageStats)
async def get_scholarship_image_stats(db: Session = Depends(get_db)):
    """Get scholarship image processing statistics"""
    try:
        # Count totals
        total = db.query(Scholarship).count()
        with_websites = (
            db.query(Scholarship).filter(Scholarship.website_url.isnot(None)).count()
        )
        with_images = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_url.isnot(None))
            .count()
        )

        # Count by status
        success_count = (
            db.query(Scholarship)
            .filter(
                Scholarship.image_extraction_status == ImageExtractionStatus.SUCCESS
            )
            .count()
        )

        pending_count = (
            db.query(Scholarship)
            .filter(
                (Scholarship.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Scholarship.image_extraction_status.is_(None))
            )
            .count()
        )

        failed_count = (
            db.query(Scholarship)
            .filter(Scholarship.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        # Quality counts
        high_quality_count = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_quality_score >= 70)
            .count()
        )

        good_quality_count = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_quality_score >= 50)
            .count()
        )

        # Calculate rates
        success_rate = f"{success_count/total*100:.1f}%" if total > 0 else "0.0%"
        high_quality_rate = (
            f"{high_quality_count/with_images*100:.1f}%" if with_images > 0 else "0.0%"
        )

        return ScholarshipImageStats(
            total_scholarships=total,
            with_websites=with_websites,
            with_images=with_images,
            success_count=success_count,
            pending_count=pending_count,
            failed_count=failed_count,
            high_quality_count=high_quality_count,
            good_quality_count=good_quality_count,
            success_rate=success_rate,
            high_quality_rate=high_quality_rate,
        )

    except Exception as e:
        logger.error(f"Error getting scholarship image stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )


@router.get("/list", response_model=List[ScholarshipImageStatus])
async def list_scholarship_image_status(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(
        None, description="Filter by status: success, pending, failed"
    ),
    has_images_only: bool = Query(
        False, description="Only show scholarships with images"
    ),
    db: Session = Depends(get_db),
):
    """List scholarships with their image status"""
    try:
        query = db.query(Scholarship)

        # Apply filters
        if status_filter:
            if status_filter.lower() == "success":
                query = query.filter(
                    Scholarship.image_extraction_status == ImageExtractionStatus.SUCCESS
                )
            elif status_filter.lower() == "pending":
                query = query.filter(
                    (
                        Scholarship.image_extraction_status
                        == ImageExtractionStatus.PENDING
                    )
                    | (Scholarship.image_extraction_status.is_(None))
                )
            elif status_filter.lower() == "failed":
                query = query.filter(
                    Scholarship.image_extraction_status == ImageExtractionStatus.FAILED
                )

        if has_images_only:
            query = query.filter(Scholarship.primary_image_url.isnot(None))

        scholarships = query.offset(skip).limit(limit).all()

        results = []
        for scholarship in scholarships:
            results.append(
                ScholarshipImageStatus(
                    id=scholarship.id,
                    title=scholarship.title,
                    organization=scholarship.organization,
                    website_url=scholarship.website_url,
                    primary_image_url=scholarship.primary_image_url,
                    primary_image_quality_score=scholarship.primary_image_quality_score,
                    logo_image_url=scholarship.logo_image_url,
                    image_extraction_status=(
                        scholarship.image_extraction_status.value
                        if scholarship.image_extraction_status
                        else "PENDING"
                    ),
                    image_extraction_date=scholarship.image_extraction_date,
                )
            )

        return results

    except Exception as e:
        logger.error(f"Error listing scholarship image status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scholarships: {str(e)}",
        )


@router.post("/extract-batch", response_model=ScholarshipBatchProcessingResponse)
async def extract_scholarship_images_batch(
    background_tasks: BackgroundTasks,
    scholarship_ids: Optional[List[int]] = None,
    limit: Optional[int] = Query(
        None, description="Limit number of scholarships to process"
    ),
    run_in_background: bool = Query(False, description="Run extraction in background"),
    force_reprocess: bool = Query(
        False, description="Force reprocess scholarships that already have images"
    ),
    db: Session = Depends(get_db),
):
    """
    Extract images for scholarships in batch

    Features:
    - Process specific scholarship IDs or all pending/failed
    - Extracts organization logos and program imagery
    - Scores images based on organization relevance
    - Uploads to CDN and updates database
    """
    try:
        batch_id = f"scholarship_batch_{int(datetime.now().timestamp())}"

        # Validate scholarship IDs if provided
        if scholarship_ids:
            existing_count = (
                db.query(Scholarship)
                .filter(Scholarship.id.in_(scholarship_ids))
                .count()
            )
            if existing_count != len(scholarship_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Some scholarship IDs not found. Found {existing_count}, expected {len(scholarship_ids)}",
                )

        # Build query to count scholarships to process
        query = db.query(Scholarship)
        if scholarship_ids:
            query = query.filter(Scholarship.id.in_(scholarship_ids))
        else:
            if force_reprocess:
                query = query.filter(Scholarship.website_url.isnot(None))
            else:
                query = query.filter(
                    (
                        Scholarship.image_extraction_status
                        == ImageExtractionStatus.PENDING
                    )
                    | (
                        Scholarship.image_extraction_status
                        == ImageExtractionStatus.FAILED
                    )
                    | (Scholarship.image_extraction_status.is_(None))
                ).filter(Scholarship.website_url.isnot(None))

        if limit:
            query = query.limit(limit)

        scholarships_to_process = query.count()

        if scholarships_to_process == 0:
            return ScholarshipBatchProcessingResponse(
                batch_id=batch_id,
                total_processed=0,
                successful=0,
                failed=0,
                no_website=0,
                org_logos_found=0,
                stats={"message": "No scholarships found to process"},
                results=[],
            )

        logger.info(
            f"Scholarship batch processing: {scholarships_to_process} scholarships"
        )

        if run_in_background:
            # Run in background
            background_tasks.add_task(
                run_scholarship_extraction_background,
                scholarship_ids,
                limit,
                force_reprocess,
                db,
            )

            return ScholarshipBatchProcessingResponse(
                batch_id=batch_id,
                total_processed=scholarships_to_process,
                successful=0,
                failed=0,
                no_website=0,
                org_logos_found=0,
                stats={"status": "running_in_background"},
                results=[],
            )
        else:
            # Run synchronously
            extractor = ScholarshipImageExtractor(db)
            result = extractor.process_scholarships_batch(
                scholarship_ids=scholarship_ids,
                limit=limit,
                force_reprocess=force_reprocess,
            )

            # Convert results to API format
            api_results = []
            for res in result.get("results", []):
                api_results.append(
                    ScholarshipImageResult(
                        scholarship_id=res["scholarship_id"],
                        title=res["title"],
                        organization=res["organization"],
                        status=res["status"],
                        cdn_urls=res.get("cdn_urls", {}),
                        quality_score=res.get("best_image", {}).get("quality_score"),
                        error=res.get("error"),
                    )
                )

            return ScholarshipBatchProcessingResponse(
                batch_id=batch_id,
                total_processed=result["total_processed"],
                successful=result["successful"],
                failed=result["failed"],
                no_website=result["no_website"],
                org_logos_found=result["org_logos_found"],
                stats=result["stats"],
                results=api_results,
            )

    except Exception as e:
        logger.error(f"Error in extract_scholarship_images_batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process scholarship images: {str(e)}",
        )


@router.post("/extract-single/{scholarship_id}", response_model=ScholarshipImageResult)
async def extract_single_scholarship_image(
    scholarship_id: int,
    force_reprocess: bool = Query(
        False, description="Force reprocess even if already has images"
    ),
    db: Session = Depends(get_db),
):
    """Extract images for a single scholarship"""
    try:
        # Get the scholarship
        scholarship = (
            db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )
        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship with ID {scholarship_id} not found",
            )

        # Check if already processed
        if (
            not force_reprocess
            and scholarship.image_extraction_status == ImageExtractionStatus.SUCCESS
        ):
            return ScholarshipImageResult(
                scholarship_id=scholarship.id,
                title=scholarship.title,
                organization=scholarship.organization,
                status="already_processed",
                cdn_urls={"primary": scholarship.primary_image_url or ""},
                quality_score=scholarship.primary_image_quality_score,
            )

        # Process the scholarship
        extractor = ScholarshipImageExtractor(db)
        result = extractor.process_scholarship(scholarship)

        return ScholarshipImageResult(
            scholarship_id=result["scholarship_id"],
            title=result["title"],
            organization=result["organization"],
            status=result["status"],
            cdn_urls=result.get("cdn_urls", {}),
            quality_score=result.get("best_image", {}).get("quality_score"),
            error=result.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing single scholarship {scholarship_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process scholarship: {str(e)}",
        )


@router.delete("/clear-images/{scholarship_id}")
async def clear_scholarship_images(
    scholarship_id: int,
    db: Session = Depends(get_db),
):
    """Clear images for a specific scholarship (useful for reprocessing)"""
    try:
        scholarship = (
            db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )
        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship with ID {scholarship_id} not found",
            )

        # Clear image data
        scholarship.primary_image_url = None
        scholarship.primary_image_quality_score = None
        scholarship.logo_image_url = None
        scholarship.image_extraction_status = ImageExtractionStatus.PENDING
        scholarship.image_extraction_date = None

        db.commit()

        return {
            "message": f"Cleared images for scholarship '{scholarship.title}'",
            "scholarship_id": scholarship_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing scholarship images for {scholarship_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear images: {str(e)}",
        )


@router.post("/reset-failed")
async def reset_failed_scholarships(db: Session = Depends(get_db)):
    """Reset all failed scholarship extractions to pending (useful for retry)"""
    try:
        failed_count = (
            db.query(Scholarship)
            .filter(Scholarship.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        db.query(Scholarship).filter(
            Scholarship.image_extraction_status == ImageExtractionStatus.FAILED
        ).update(
            {
                Scholarship.image_extraction_status: ImageExtractionStatus.PENDING,
                Scholarship.image_extraction_date: None,
            }
        )

        db.commit()

        return {
            "message": f"Reset {failed_count} failed scholarships to pending status",
            "count": failed_count,
        }

    except Exception as e:
        logger.error(f"Error resetting failed scholarships: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset failed scholarships: {str(e)}",
        )
