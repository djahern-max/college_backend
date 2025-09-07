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

# Web scraping imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from PIL import Image
import io

from app.core.database import get_db
from app.services.image_extractor import MagicScholarImageExtractor
from app.services.institution import InstitutionService
from app.schemas.image_batch import (
    BatchUploadRequest,
    BatchUploadResponse,
    ProcessingStats,
    ImageQualityFilter,
    ImageProcessingStatus,
)
from app.models.institution import Institution
from app.services.image_extractor import ImageUploadService

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


# NEW EXTRACTION ENDPOINTS


@router.get("/test-csv-load")
async def test_csv_load():
    """Test if we can load the sample CSV"""
    csv_path = "data/raw_data/image_upload_sample.csv"

    if not Path(csv_path).exists():
        raise HTTPException(status_code=404, detail=f"CSV not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
        first_school = df.iloc[0].to_dict()

        return {
            "status": "success",
            "total_schools": len(df),
            "first_school": first_school,
            "columns": list(df.columns),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")


@router.post("/extract-from-csv")
async def extract_from_csv(max_schools: int = 3, db: Session = Depends(get_db)):
    """Extract images from CSV sample and upload to Digital Ocean"""

    csv_path = "data/raw_data/image_upload_sample.csv"

    if not Path(csv_path).exists():
        raise HTTPException(status_code=404, detail=f"CSV not found: {csv_path}")

    try:
        # Load CSV
        df = pd.read_csv(csv_path).head(max_schools)
        upload_service = ImageUploadService(db)

        results = []

        for _, row in df.iterrows():
            school_name = row["name"]
            website = str(row["website"]).strip()
            ipeds_id = row["ipeds_id"]

            # Find institution in database
            institution = (
                db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
            )
            if not institution:
                results.append(
                    {
                        "name": school_name,
                        "status": "not_found_in_db",
                        "ipeds_id": ipeds_id,
                    }
                )
                continue

            # Clean URL
            if not website.startswith(("http://", "https://")):
                website = "https://" + website

            logger.info(f"Processing: {school_name} ({website})")

            try:
                # Extract images from website
                response = requests.get(website, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                # Look for Open Graph image
                og_image = soup.find("meta", property="og:image")
                if og_image and og_image.get("content"):
                    img_url = urljoin(website, og_image.get("content"))

                    # Download image
                    img_response = requests.get(img_url, timeout=10)
                    img_response.raise_for_status()

                    if img_response.headers.get("content-type", "").startswith(
                        "image/"
                    ):
                        image_data = img_response.content

                        # Get image dimensions
                        with Image.open(io.BytesIO(image_data)) as img:
                            width, height = img.size

                        if width >= 200 and height >= 200:  # Basic quality filter
                            # Prepare for upload
                            batch_data = [
                                {
                                    "ipeds_id": ipeds_id,
                                    "name": school_name,
                                    "images": {
                                        "primary": {
                                            "data": image_data,
                                            "type": "og_image",
                                            "width": width,
                                            "height": height,
                                            "size_bytes": len(image_data),
                                        }
                                    },
                                }
                            ]

                            # Upload using existing service
                            upload_results = upload_service.process_institution_images(
                                batch_data
                            )

                            results.append(
                                {
                                    "name": school_name,
                                    "status": "success",
                                    "ipeds_id": ipeds_id,
                                    "image_url": img_url,
                                    "upload_result": upload_results,
                                }
                            )
                        else:
                            results.append(
                                {
                                    "name": school_name,
                                    "status": "image_too_small",
                                    "ipeds_id": ipeds_id,
                                    "dimensions": f"{width}x{height}",
                                }
                            )
                    else:
                        results.append(
                            {
                                "name": school_name,
                                "status": "invalid_image",
                                "ipeds_id": ipeds_id,
                            }
                        )
                else:
                    results.append(
                        {
                            "name": school_name,
                            "status": "no_og_image",
                            "ipeds_id": ipeds_id,
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "name": school_name,
                        "status": "failed",
                        "ipeds_id": ipeds_id,
                        "error": str(e),
                    }
                )

            # Be respectful with delays
            time.sleep(1)

        return {
            "status": "completed",
            "processed": len(results),
            "results": results,
            "csv_path": csv_path,
        }

    except Exception as e:
        logger.error(f"CSV extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/test-single-extraction")
async def test_single_extraction(ipeds_id: int, db: Session = Depends(get_db)):
    """Test extraction on a single school"""

    try:
        # Find institution
        institution = (
            db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
        )
        if not institution:
            raise HTTPException(
                status_code=404, detail=f"Institution {ipeds_id} not found"
            )

        website = institution.website
        if not website:
            return {"status": "no_website", "institution": institution.name}

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        try:
            response = requests.get(website, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for images
            og_image = soup.find("meta", property="og:image")
            images_found = []

            if og_image and og_image.get("content"):
                images_found.append(
                    {
                        "type": "og_image",
                        "url": urljoin(website, og_image.get("content")),
                    }
                )

            return {
                "status": "success",
                "institution": {
                    "name": institution.name,
                    "website": website,
                    "ipeds_id": ipeds_id,
                },
                "images_found": images_found,
            }

        except Exception as e:
            return {
                "status": "extraction_failed",
                "institution": institution.name,
                "error": str(e),
            }

    except Exception as e:
        logger.error(f"Error testing extraction for {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
