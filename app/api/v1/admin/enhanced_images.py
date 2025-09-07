# app/api/v1/admin/enhanced_images.py
"""
Enhanced Image Processing API with deletion and improved extraction
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.services.enhanced_image_extractor import EnhancedImageExtractor
from app.models.institution import Institution, ImageExtractionStatus
from app.schemas.image_batch import BatchProcessingResponse, ProcessingStatsResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract-enhanced-batch", response_model=BatchProcessingResponse)
async def extract_enhanced_images_batch(
    background_tasks: BackgroundTasks,
    institution_ids: Optional[List[int]] = None,
    limit: Optional[int] = Query(
        None, description="Limit number of institutions to process"
    ),
    run_in_background: bool = Query(False, description="Run extraction in background"),
    force_reprocess: bool = Query(
        False, description="Force reprocess institutions that already have images"
    ),
    db: Session = Depends(get_db),
):
    """
    Enhanced image extraction with Digital Ocean Spaces deletion and improved OG image detection

    Features:
    - Automatically deletes existing images before uploading new ones
    - Enhanced OG image and Twitter card detection
    - Improved campus imagery prioritization
    - Better quality scoring for university images
    """
    try:
        batch_id = f"enhanced_batch_{int(datetime.now().timestamp())}"

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
                    detail=f"Some institution IDs not found. Found {existing_count}, expected {len(institution_ids)}",
                )

        # Build query
        query = db.query(Institution)

        if institution_ids:
            query = query.filter(Institution.ipeds_id.in_(institution_ids))
        else:
            if force_reprocess:
                # Process all institutions with websites
                query = query.filter(Institution.website.isnot(None))
            else:
                # Only process institutions that haven't been processed or failed
                query = query.filter(
                    (
                        Institution.image_extraction_status
                        == ImageExtractionStatus.PENDING
                    )
                    | (
                        Institution.image_extraction_status
                        == ImageExtractionStatus.FAILED
                    )
                    | (Institution.image_extraction_status.is_(None))
                ).filter(Institution.website.isnot(None))

        if limit:
            query = query.limit(limit)

        institutions_to_process = query.count()

        if institutions_to_process == 0:
            return BatchProcessingResponse(
                batch_id=batch_id,
                total_processed=0,
                successful=0,
                failed=0,
                no_images=0,
                no_website=0,
                stats={"message": "No institutions found to process"},
                results=[],
            )

        logger.info(
            f"Enhanced batch processing: {institutions_to_process} institutions"
        )

        if run_in_background:
            # Run in background
            background_tasks.add_task(
                run_enhanced_extraction_batch,
                institution_ids or [],
                limit,
                force_reprocess,
                db,
            )

            return BatchProcessingResponse(
                batch_id=batch_id,
                total_processed=institutions_to_process,
                successful=0,
                failed=0,
                no_images=0,
                no_website=0,
                stats={"status": "running_in_background"},
                results=[],
            )
        else:
            # Run synchronously
            extractor = EnhancedImageExtractor(db)

            # Override query parameters for the extractor
            if force_reprocess:
                result = extractor.process_institutions_batch(
                    institution_ids=institution_ids, limit=limit, force_reprocess=True
                )
            else:
                result = extractor.process_institutions_batch(
                    institution_ids=institution_ids, limit=limit
                )

            # Convert results to API format
            api_results = []
            for res in result.get("results", []):
                api_results.append(
                    {
                        "institution_id": res["institution_id"],
                        "name": res["name"],
                        "status": res["status"],
                        "cdn_urls": res.get("cdn_urls", {}),
                        "quality_score": res.get("best_image", {}).get("quality_score"),
                        "error": res.get("error"),
                    }
                )

            return BatchProcessingResponse(
                batch_id=batch_id,
                total_processed=result["total_processed"],
                successful=result["successful"],
                failed=result["failed"],
                no_images=result.get("no_images", 0),
                no_website=result.get("no_website", 0),
                stats=result["stats"],
                results=api_results,
            )

    except Exception as e:
        logger.error(f"Enhanced batch processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced batch processing failed: {str(e)}",
        )


@router.post("/extract-enhanced-single/{institution_id}")
async def extract_enhanced_single_institution(
    institution_id: int,
    force_reprocess: bool = Query(
        False, description="Force reprocess even if images exist"
    ),
    db: Session = Depends(get_db),
):
    """Extract images for a single institution using enhanced extraction with deletion"""
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

        # Check if already processed (unless forcing reprocess)
        if (
            not force_reprocess
            and institution.image_extraction_status == ImageExtractionStatus.SUCCESS
        ):
            return {
                "message": f"Institution {institution.name} already has images. Use force_reprocess=true to reprocess.",
                "current_image_url": institution.primary_image_url,
                "current_quality_score": institution.primary_image_quality_score,
            }

        # Create enhanced extractor and process
        extractor = EnhancedImageExtractor(db)
        result = extractor.process_institution(institution)

        return {
            "institution_id": result["institution_id"],
            "name": result["name"],
            "status": result["status"],
            "cdn_urls": result.get("cdn_urls", {}),
            "best_image": result.get("best_image"),
            "images_found": len(result.get("images", {})),
            "processing_time": result.get("processed_at"),
            "error": result.get("error"),
        }

    except Exception as e:
        logger.error(f"Enhanced single institution processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced processing failed: {str(e)}",
        )


@router.delete("/delete-institution-images/{institution_id}")
async def delete_institution_images(institution_id: int, db: Session = Depends(get_db)):
    """Delete all images for a specific institution from Digital Ocean Spaces and database"""
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

        # Create enhanced extractor for spaces management
        extractor = EnhancedImageExtractor(db)

        # Delete from Digital Ocean Spaces
        deletion_success = extractor.spaces_manager.delete_existing_images(
            institution.name
        )

        # Clear database fields
        institution.primary_image_url = None
        institution.primary_image_quality_score = None
        institution.logo_image_url = None
        institution.image_extraction_status = ImageExtractionStatus.PENDING
        institution.image_extraction_date = None

        db.commit()

        return {
            "message": f"Successfully deleted images for {institution.name}",
            "institution_id": institution_id,
            "spaces_deletion_success": deletion_success,
            "database_cleared": True,
        }

    except Exception as e:
        logger.error(f"Image deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image deletion failed: {str(e)}",
        )


@router.get("/processing-stats", response_model=ProcessingStatsResponse)
async def get_enhanced_processing_stats(db: Session = Depends(get_db)):
    """Get comprehensive statistics about image processing status"""
    try:
        # Total institutions
        total_institutions = db.query(Institution).count()

        # Institutions with images
        with_images = (
            db.query(Institution)
            .filter(Institution.primary_image_url.isnot(None))
            .count()
        )

        # High quality images (80+)
        high_quality = (
            db.query(Institution)
            .filter(Institution.primary_image_quality_score >= 80)
            .count()
        )

        # Good quality images (60+)
        good_quality = (
            db.query(Institution)
            .filter(Institution.primary_image_quality_score >= 60)
            .count()
        )

        # Pending processing
        pending = (
            db.query(Institution)
            .filter(
                (Institution.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Institution.image_extraction_status.is_(None))
            )
            .count()
        )

        # Failed processing
        failed = (
            db.query(Institution)
            .filter(Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        # Calculate rates
        success_rate = (
            f"{(with_images / total_institutions * 100):.1f}%"
            if total_institutions > 0
            else "0%"
        )
        high_quality_rate = (
            f"{(high_quality / with_images * 100):.1f}%" if with_images > 0 else "0%"
        )

        return ProcessingStatsResponse(
            total_institutions=total_institutions,
            with_images=with_images,
            high_quality_images=high_quality,
            good_quality_images=good_quality,
            pending_processing=pending,
            failed_processing=failed,
            success_rate=success_rate,
            high_quality_rate=high_quality_rate,
        )

    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}",
        )


@router.post("/retry-failed-enhanced")
async def retry_failed_enhanced_extractions(
    limit: Optional[int] = Query(
        50, description="Max number of failed institutions to retry"
    ),
    db: Session = Depends(get_db),
):
    """Retry failed extractions using enhanced extraction method"""
    try:
        # Get failed institutions
        failed_institutions = (
            db.query(Institution)
            .filter(Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            .filter(Institution.website.isnot(None))
            .limit(limit)
            .all()
        )

        if not failed_institutions:
            return {"message": "No failed institutions found to retry", "retried": 0}

        # Extract IDs and retry
        institution_ids = [inst.ipeds_id for inst in failed_institutions]

        extractor = EnhancedImageExtractor(db)
        result = extractor.process_institutions_batch(institution_ids=institution_ids)

        return {
            "message": f"Retried {len(institution_ids)} failed extractions using enhanced method",
            "total_retried": len(institution_ids),
            "successful": result["successful"],
            "failed": result["failed"],
            "high_quality_found": result["high_quality"],
        }

    except Exception as e:
        logger.error(f"Enhanced retry error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced retry failed: {str(e)}",
        )


def run_enhanced_extraction_batch(
    institution_ids: List[int], limit: Optional[int], force_reprocess: bool, db: Session
):
    """Background task for enhanced image extraction"""
    try:
        extractor = EnhancedImageExtractor(db)
        result = extractor.process_institutions_batch(
            institution_ids=institution_ids if institution_ids else None,
            limit=limit,
            force_reprocess=force_reprocess,
        )
        logger.info(
            f"Enhanced background processing completed: {result['successful']} successful, {result['failed']} failed"
        )
        return result
    except Exception as e:
        logger.error(f"Enhanced background processing failed: {e}")
        raise
