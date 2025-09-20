# Minimal fix for your enhanced_images.py router
# Add these imports at the top:

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db, SessionLocal
from app.services.institution import InstitutionService
from app.services.image_extractor import (
    MagicScholarImageExtractor,
)  # Use existing extractor
from app.models.institution import Institution, ImageExtractionStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# Simple background task using your existing image extractor
def run_background_image_processing(institution_ids: List[int]):
    """Background task using existing MagicScholarImageExtractor"""
    db = SessionLocal()
    try:
        logger.info(
            f"Starting background processing for {len(institution_ids)} institutions"
        )

        extractor = MagicScholarImageExtractor(db)
        result = extractor.process_institutions_batch(institution_ids=institution_ids)

        logger.info(
            f"Background processing completed: {result.get('successful', 0)} successful"
        )
        return result

    except Exception as e:
        logger.error(f"Background processing error: {e}")
        raise
    finally:
        db.close()


# Simplified quick-fix endpoint
@router.post("/quick-fix-missing-images")
async def quick_fix_missing_images(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(50, ge=1, le=200),
    reset_failed: bool = Query(True),
    run_in_background: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Quick fix for missing images using existing infrastructure"""
    try:
        batch_id = f"quickfix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        institution_service = InstitutionService(db)

        # Get diagnostics if the method exists
        try:
            diagnostics = institution_service.get_image_processing_diagnostics()
        except AttributeError:
            # Fallback if diagnostic method doesn't exist yet
            diagnostics = {
                "message": "Diagnostics not available - add diagnostic methods to InstitutionService"
            }

        # Reset failed statuses if requested
        reset_count = 0
        if reset_failed:
            try:
                reset_count = institution_service.bulk_reset_failed_image_processing()
            except AttributeError:
                # Fallback reset method
                reset_count = (
                    db.query(Institution)
                    .filter(
                        Institution.image_extraction_status
                        == ImageExtractionStatus.FAILED
                    )
                    .update(
                        {
                            Institution.image_extraction_status: ImageExtractionStatus.PENDING
                        }
                    )
                )
                db.commit()

        # Get institutions that need processing
        # Use your existing base query method for institutions with tuition data
        institutions_query = institution_service._build_base_query_with_tuition_filter()

        # Filter for institutions that need processing
        ready_institutions = (
            institutions_query.filter(Institution.website.isnot(None))
            .filter(Institution.website != "")
            .filter(
                (Institution.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Institution.image_extraction_status == ImageExtractionStatus.FAILED)
                | (Institution.image_extraction_status.is_(None))
                | (Institution.primary_image_url.is_(None))
            )
            .order_by(Institution.customer_rank.desc().nulls_last(), Institution.name)
            .limit(batch_size)
            .all()
        )

        if not ready_institutions:
            return {
                "message": "No institutions ready for processing",
                "batch_id": batch_id,
                "reset_count": reset_count,
                "ready_count": 0,
            }

        institution_ids = [inst.ipeds_id for inst in ready_institutions]

        logger.info(f"Found {len(institution_ids)} institutions ready for processing")

        if run_in_background:
            # Run in background
            background_tasks.add_task(run_background_image_processing, institution_ids)

            return {
                "message": f"Started background processing for {len(institution_ids)} institutions",
                "batch_id": batch_id,
                "reset_count": reset_count,
                "processing_institutions": [
                    {"ipeds_id": inst.ipeds_id, "name": inst.name}
                    for inst in ready_institutions[:10]  # Show first 10
                ],
                "total_queued": len(institution_ids),
                "status": "background_processing_started",
            }
        else:
            # Process synchronously (for smaller batches)
            extractor = MagicScholarImageExtractor(db)
            result = extractor.process_institutions_batch(
                institution_ids=institution_ids
            )

            return {
                "message": f"Completed processing {len(institution_ids)} institutions",
                "batch_id": batch_id,
                "reset_count": reset_count,
                "result": result,
            }

    except Exception as e:
        logger.error(f"Quick fix error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick fix failed: {str(e)}",
        )


# Simple diagnostics endpoint
@router.get("/simple-diagnostics")
async def get_simple_diagnostics(db: Session = Depends(get_db)):
    """Get simple diagnostics about image processing status"""
    try:
        institution_service = InstitutionService(db)

        # Count institutions with tuition data
        total_with_tuition = (
            institution_service._build_base_query_with_tuition_filter().count()
        )

        # Count with images
        with_images = (
            institution_service._build_base_query_with_tuition_filter()
            .filter(Institution.primary_image_url.isnot(None))
            .count()
        )

        # Count without images
        without_images = total_with_tuition - with_images

        # Count by status
        pending = (
            institution_service._build_base_query_with_tuition_filter()
            .filter(
                Institution.image_extraction_status == ImageExtractionStatus.PENDING
            )
            .count()
        )

        failed = (
            institution_service._build_base_query_with_tuition_filter()
            .filter(Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        no_status = (
            institution_service._build_base_query_with_tuition_filter()
            .filter(Institution.image_extraction_status.is_(None))
            .count()
        )

        no_website = (
            institution_service._build_base_query_with_tuition_filter()
            .filter((Institution.website.is_(None)) | (Institution.website == ""))
            .count()
        )

        ready_for_processing = (
            institution_service._build_base_query_with_tuition_filter()
            .filter(Institution.website.isnot(None))
            .filter(Institution.website != "")
            .filter(
                (Institution.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Institution.image_extraction_status == ImageExtractionStatus.FAILED)
                | (Institution.image_extraction_status.is_(None))
                | (Institution.primary_image_url.is_(None))
            )
            .count()
        )

        return {
            "institutions_with_tuition_data": {
                "total": total_with_tuition,
                "with_images": with_images,
                "without_images": without_images,
                "coverage_rate": (
                    f"{(with_images/total_with_tuition)*100:.1f}%"
                    if total_with_tuition > 0
                    else "0%"
                ),
            },
            "processing_status": {
                "pending": pending,
                "failed": failed,
                "no_status": no_status,
                "no_website": no_website,
                "ready_for_processing": ready_for_processing,
            },
            "recommendations": [
                f"Process {ready_for_processing} institutions ready for image extraction",
                (
                    f"Manual intervention needed for {no_website} institutions without websites"
                    if no_website > 0
                    else None
                ),
                f"Reset {failed} failed institutions and retry" if failed > 0 else None,
            ],
        }

    except Exception as e:
        logger.error(f"Error getting diagnostics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get diagnostics: {str(e)}",
        )
