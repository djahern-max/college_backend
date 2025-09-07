# app/api/v1/admin/__init__.py
# Empty file to make it a package

# app/api/v1/admin/images.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import uuid
import tempfile
import json
import base64
from pathlib import Path

from app.core.database import get_db
from app.services.image_upload import ImageUploadService
from app.services.institution import InstitutionService
from app.schemas.image_batch import (
    BatchUploadRequest,
    BatchUploadResponse,
    ProcessingStats,
    ImageQualityFilter,
    ImageProcessingStatus,
)
from app.models.institution import Institution

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-batch", response_model=BatchUploadResponse)
async def upload_image_batch(
    batch_request: BatchUploadRequest, db: Session = Depends(get_db)
):
    """
    Upload and process a batch of institution images
    This endpoint accepts image data, uploads to Digital Ocean Spaces,
    and updates the database with URLs and quality scores
    """
    start_time = time.time()
    batch_id = f"batch_{int(time.time())}_{str(uuid.uuid4())[:8]}"

    try:
        upload_service = ImageUploadService(db)

        # Convert the request data to the format expected by the service
        batch_data = []

        for institution in batch_request.institutions:
            # Convert base64 image data back to bytes
            images = {}
            for img_type, img_data in institution.images.items():
                if isinstance(img_data.data, str):
                    # Assume base64 encoded
                    try:
                        image_bytes = base64.b64decode(img_data.data)
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid base64 data for {institution.name} {img_type}: {e}",
                        )
                else:
                    image_bytes = img_data.data

                images[img_type] = {
                    "data": image_bytes,
                    "type": img_data.type,
                    "width": img_data.width,
                    "height": img_data.height,
                    "size_bytes": img_data.size_bytes,
                }

            batch_data.append(
                {
                    "ipeds_id": institution.ipeds_id,
                    "name": institution.name,
                    "images": images,
                }
            )

        # Process the batch
        results = upload_service.process_institution_images(batch_data)

        processing_time = time.time() - start_time

        return BatchUploadResponse(
            success=results["failed"] == 0,
            processed=results["processed"],
            failed=results["failed"],
            batch_id=batch_id,
            uploaded_urls=results["uploaded_urls"],
            errors=results["errors"],
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}",
        )


@router.post("/upload-files-batch")
async def upload_files_batch(
    files: List[UploadFile] = File(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Alternative endpoint for uploading files directly with metadata
    Metadata should be JSON string with institution info
    """
    try:
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON in metadata",
            )

        upload_service = ImageUploadService(db)
        batch_data = []

        # Process uploaded files
        for i, file in enumerate(files):
            if i >= len(metadata_dict.get("institutions", [])):
                break

            institution_meta = metadata_dict["institutions"][i]

            # Read file data
            file_data = await file.read()

            # Get image dimensions using PIL
            from PIL import Image
            import io

            try:
                with Image.open(io.BytesIO(file_data)) as img:
                    width, height = img.size
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid image file: {file.filename}",
                )

            # Create batch data entry
            images = {
                "primary": {
                    "data": file_data,
                    "type": institution_meta.get("image_type", "og_image"),
                    "width": width,
                    "height": height,
                    "size_bytes": len(file_data),
                }
            }

            batch_data.append(
                {
                    "ipeds_id": institution_meta["ipeds_id"],
                    "name": institution_meta["name"],
                    "images": images,
                }
            )

        # Process the batch
        results = upload_service.process_institution_images(batch_data)

        return {
            "processed": results["processed"],
            "failed": results["failed"],
            "errors": results["errors"],
            "uploaded_urls": results["uploaded_urls"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File batch upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )


@router.get("/stats", response_model=ProcessingStats)
async def get_processing_stats(db: Session = Depends(get_db)):
    """Get current image processing statistics"""
    try:
        upload_service = ImageUploadService(db)
        stats = upload_service.get_processing_stats()

        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=stats["error"]
            )

        return ProcessingStats(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing stats: {str(e)}",
        )


@router.get("/status", response_model=List[ImageProcessingStatus])
async def get_processing_status(
    filter_params: ImageQualityFilter = Depends(),
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db),
):
    """Get processing status for institutions with optional filtering"""
    try:
        query = db.query(Institution)

        # Apply filters
        if filter_params.min_quality_score is not None:
            query = query.filter(
                Institution.primary_image_quality_score
                >= filter_params.min_quality_score
            )

        if filter_params.max_quality_score is not None:
            query = query.filter(
                Institution.primary_image_quality_score
                <= filter_params.max_quality_score
            )

        if filter_params.has_primary_image is not None:
            if filter_params.has_primary_image:
                query = query.filter(Institution.primary_image_url.isnot(None))
            else:
                query = query.filter(Institution.primary_image_url.is_(None))

        if filter_params.has_logo is not None:
            if filter_params.has_logo:
                query = query.filter(Institution.logo_image_url.isnot(None))
            else:
                query = query.filter(Institution.logo_image_url.is_(None))

        if filter_params.extraction_status:
            query = query.filter(
                Institution.image_extraction_status == filter_params.extraction_status
            )

        # Apply pagination
        offset = (page - 1) * per_page
        institutions = query.offset(offset).limit(per_page).all()

        # Convert to response format
        result = []
        for institution in institutions:
            result.append(
                ImageProcessingStatus(
                    ipeds_id=institution.ipeds_id,
                    name=institution.name,
                    primary_image_url=institution.primary_image_url,
                    primary_image_quality_score=institution.primary_image_quality_score,
                    logo_image_url=institution.logo_image_url,
                    image_extraction_status=institution.image_extraction_status,
                    image_extraction_date=institution.image_extraction_date,
                )
            )

        return result

    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing status: {str(e)}",
        )


@router.post("/cleanup")
async def cleanup_temp_files():
    """Manual cleanup endpoint for temporary files"""
    try:
        temp_dir = Path(tempfile.gettempdir()) / "magicscholar_images"
        if temp_dir.exists():
            import shutil

            shutil.rmtree(temp_dir)
            return {"message": "Temporary files cleaned up successfully"}
        else:
            return {"message": "No temporary files to clean up"}

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}",
        )


@router.get("/pending")
async def get_pending_institutions(limit: int = 100, db: Session = Depends(get_db)):
    """Get institutions that still need image processing"""
    try:
        from app.models.institution import ImageExtractionStatus

        pending = (
            db.query(Institution)
            .filter(
                Institution.image_extraction_status.in_(
                    [ImageExtractionStatus.PENDING, None]
                )
            )
            .limit(limit)
            .all()
        )

        result = []
        for institution in pending:
            result.append(
                {
                    "ipeds_id": institution.ipeds_id,
                    "name": institution.name,
                    "website": institution.website,
                    "state": institution.state,
                    "control_type": institution.control_type,
                }
            )

        return {"pending_count": len(result), "institutions": result}

    except Exception as e:
        logger.error(f"Error getting pending institutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending institutions: {str(e)}",
        )
