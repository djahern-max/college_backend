# app/services/image_upload.py
import boto3
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import io
import hashlib
from sqlalchemy.orm import Session

from app.models.institution import Institution, ImageExtractionStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageUploadService:
    """Service for uploading images to Digital Ocean Spaces and updating database"""

    def __init__(self, db: Session):
        self.db = db
        self.session = boto3.session.Session()
        self.client = self.session.client(
            "s3",
            region_name=os.getenv("DIGITAL_OCEAN_SPACES_REGION"),
            endpoint_url=os.getenv("DIGITAL_OCEAN_SPACES_ENDPOINT"),
            aws_access_key_id=os.getenv("DIGITAL_OCEAN_SPACES_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("DIGITAL_OCEAN_SPACES_SECRET_KEY"),
        )
        self.bucket_name = os.getenv("DIGITAL_OCEAN_SPACES_BUCKET")
        self.cdn_base_url = os.getenv("IMAGE_CDN_BASE_URL")

        # Image standardization settings (same as IPEDS processor)
        self.target_width = 400
        self.target_height = 300

    def calculate_image_quality_score(
        self, image_info: Dict[str, Any], image_type: str
    ) -> int:
        """Calculate quality score using the same algorithm as IPEDS processor"""
        score = 0
        width = image_info.get("width", 0)
        height = image_info.get("height", 0)
        size_bytes = image_info.get("size_bytes", 0)

        # Size quality (40 points max)
        if width >= 1200:
            score += 20
        elif width >= 800:
            score += 15
        elif width >= 600:
            score += 10
        elif width >= 400:
            score += 5

        if height >= 600:
            score += 20
        elif height >= 400:
            score += 15
        elif height >= 300:
            score += 10
        elif height >= 200:
            score += 5

        # Aspect ratio quality (20 points max)
        if width > 0 and height > 0:
            ratio = width / height
            if 1.2 <= ratio <= 2.5:  # Good for cards
                score += 20
            elif 1.0 <= ratio <= 3.0:  # Acceptable
                score += 10

        # File size quality (20 points max)
        if size_bytes > 200000:
            score += 20  # Large, detailed
        elif size_bytes > 100000:
            score += 15  # Good size
        elif size_bytes > 50000:
            score += 10  # Acceptable
        elif size_bytes > 20000:
            score += 5  # Small but usable

        # Image type bonus (20 points max)
        type_bonuses = {
            "og_image": 20,  # Usually best quality
            "hero": 15,  # Good campus images
            "twitter_image": 12,  # Decent quality
            "logo": 8,  # Useful but not primary
            "favicon": 3,  # Usually too small
        }
        score += type_bonuses.get(image_type, 0)

        return min(score, 100)  # Cap at 100

    def standardize_image(
        self, image_data: bytes, school_name: str, image_type: str, quality_score: int
    ) -> Tuple[bytes, str]:
        """Standardize image to consistent dimensions (same as IPEDS processor)"""
        try:
            # Open image from bytes
            img = Image.open(io.BytesIO(image_data))
            img = img.convert("RGB")

            # Calculate scaling to fit within target dimensions while maintaining aspect ratio
            img_ratio = img.width / img.height
            target_ratio = self.target_width / self.target_height

            if img_ratio > target_ratio:
                # Image is wider than target ratio - fit to width
                new_width = self.target_width
                new_height = int(self.target_width / img_ratio)
            else:
                # Image is taller than target ratio - fit to height
                new_height = self.target_height
                new_width = int(self.target_height * img_ratio)

            # Resize maintaining aspect ratio
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create canvas and center image
            canvas = Image.new("RGB", (self.target_width, self.target_height), "white")
            x = (self.target_width - img.width) // 2
            y = (self.target_height - img.height) // 2
            canvas.paste(img, (x, y))

            # Generate filename with quality score
            safe_school_name = "".join(
                c for c in school_name if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_school_name = safe_school_name.replace(" ", "_")[:50]

            # Include quality score in filename for easy sorting
            filename = f"{safe_school_name}_q{quality_score:02d}_{image_type}.jpg"

            # Convert to bytes
            output = io.BytesIO()
            canvas.save(output, format="JPEG", quality=85, optimize=True)
            return output.getvalue(), filename

        except Exception as e:
            logger.error(f"Failed to standardize image: {e}")
            raise

    def upload_to_spaces(self, image_data: bytes, key: str) -> str:
        """Upload image data to Digital Ocean Spaces"""
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ACL="public-read",
                ContentType="image/jpeg",
            )
            return f"{self.cdn_base_url}/{key}"
        except Exception as e:
            logger.error(f"Failed to upload {key} to Spaces: {e}")
            raise

    def process_institution_images(
        self, batch_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a batch of institution image data
        batch_data format: [
            {
                "ipeds_id": 123456,
                "name": "University Name",
                "images": {
                    "primary": {"data": bytes, "type": "og_image", "width": 1200, "height": 800, "size_bytes": 150000},
                    "logo": {"data": bytes, "type": "logo", "width": 400, "height": 400, "size_bytes": 25000}
                }
            }
        ]
        """
        results = {"processed": 0, "failed": 0, "uploaded_urls": {}, "errors": []}

        for institution_data in batch_data:
            try:
                ipeds_id = institution_data["ipeds_id"]
                name = institution_data["name"]
                images = institution_data["images"]

                # Find institution in database
                institution = (
                    self.db.query(Institution)
                    .filter(Institution.ipeds_id == ipeds_id)
                    .first()
                )

                if not institution:
                    results["errors"].append(
                        f"Institution not found: {name} (IPEDS ID: {ipeds_id})"
                    )
                    results["failed"] += 1
                    continue

                primary_url = None
                logo_url = None
                best_quality_score = 0

                # Process primary image
                if "primary" in images:
                    primary_data = images["primary"]

                    # Calculate quality score
                    quality_score = self.calculate_image_quality_score(
                        primary_data, primary_data["type"]
                    )

                    # Standardize image
                    standardized_data, filename = self.standardize_image(
                        primary_data["data"], name, primary_data["type"], quality_score
                    )

                    # Upload to Spaces
                    key = f"primary/{filename}"
                    primary_url = self.upload_to_spaces(standardized_data, key)
                    best_quality_score = quality_score

                # Process logo image
                if "logo" in images:
                    logo_data = images["logo"]

                    # Calculate quality score for logo
                    logo_quality_score = self.calculate_image_quality_score(
                        logo_data, "logo"
                    )

                    # Standardize logo
                    standardized_logo, logo_filename = self.standardize_image(
                        logo_data["data"], name, "logo", logo_quality_score
                    )

                    # Upload logo to Spaces
                    logo_key = f"logos/{logo_filename}"
                    logo_url = self.upload_to_spaces(standardized_logo, logo_key)

                # Update institution in database
                institution.update_image_info(
                    image_url=primary_url,
                    quality_score=best_quality_score,
                    logo_url=logo_url,
                    status=ImageExtractionStatus.SUCCESS,
                )

                self.db.commit()

                results["uploaded_urls"][ipeds_id] = {
                    "primary_url": primary_url,
                    "logo_url": logo_url,
                    "quality_score": best_quality_score,
                }
                results["processed"] += 1

                logger.info(
                    f"Successfully processed {name} (Score: {best_quality_score})"
                )

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(
                    f"Failed to process {institution_data.get('name', 'Unknown')}: {str(e)}"
                )
                logger.error(f"Error processing institution: {e}")
                self.db.rollback()

        return results

    def cleanup_temp_files(self, temp_dir: Path):
        """Clean up temporary files after processing"""
        try:
            import shutil

            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup {temp_dir}: {e}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current image processing statistics"""
        try:
            total = self.db.query(Institution).count()

            with_images = (
                self.db.query(Institution)
                .filter(Institution.primary_image_url.isnot(None))
                .count()
            )

            high_quality = (
                self.db.query(Institution)
                .filter(Institution.primary_image_quality_score >= 80)
                .count()
            )

            pending = (
                self.db.query(Institution)
                .filter(
                    Institution.image_extraction_status == ImageExtractionStatus.PENDING
                )
                .count()
            )

            return {
                "total_institutions": total,
                "with_images": with_images,
                "high_quality_images": high_quality,
                "pending_processing": pending,
                "completion_rate": (
                    f"{(with_images/total)*100:.1f}%" if total > 0 else "0%"
                ),
            }
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {"error": str(e)}
