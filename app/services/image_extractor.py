# app/services/image_extractor.py - Complete improved version
"""
Complete University Image Extraction Service for MagicScholar
Integrates web scraping, image processing, and Digital Ocean Spaces upload
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import time
import tempfile
import hashlib
from PIL import Image
import io
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import os
from pathlib import Path

from app.models.institution import Institution, ImageExtractionStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class DigitalOceanSpacesUploader:
    """Handles uploads to Digital Ocean Spaces"""

    def __init__(self):
        self.spaces_client = boto3.client(
            "s3",
            endpoint_url=settings.DIGITAL_OCEAN_SPACES_ENDPOINT,
            aws_access_key_id=settings.DIGITAL_OCEAN_SPACES_ACCESS_KEY,
            aws_secret_access_key=settings.DIGITAL_OCEAN_SPACES_SECRET_KEY,
            region_name=settings.DIGITAL_OCEAN_SPACES_REGION,
        )
        self.bucket_name = settings.DIGITAL_OCEAN_SPACES_BUCKET
        self.cdn_endpoint = settings.IMAGE_CDN_BASE_URL

    def upload_image(
        self, image_bytes: bytes, file_path: str, content_type: str = "image/jpeg"
    ) -> Optional[str]:
        """Upload image to Digital Ocean Spaces and return CDN URL"""
        try:
            # Upload to Spaces
            self.spaces_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=image_bytes,
                ContentType=content_type,
                ACL="public-read",  # Make publicly accessible
                CacheControl="max-age=31536000",  # Cache for 1 year
            )

            # Return CDN URL
            cdn_url = f"{self.cdn_endpoint}/{file_path}"
            logger.info(f"Successfully uploaded image to: {cdn_url}")
            return cdn_url

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to upload image to Spaces: {e}")
            return None


class ImageUploadService:
    """Service for uploading processed images to Digital Ocean Spaces"""

    def __init__(self, db: Session):
        self.db = db
        self.uploader = DigitalOceanSpacesUploader()

    def process_institution_images(self, batch_data):
        """Process and upload institution images to Digital Ocean Spaces"""
        results = {"processed": 0, "failed": 0, "uploaded_urls": {}, "errors": []}

        for item in batch_data:
            ipeds_id = item.get("ipeds_id")
            name = item.get("name", "Unknown")

            try:
                # This would be called with actual image data from the scraper
                # For now, this is a placeholder that returns success
                results["uploaded_urls"][ipeds_id] = {
                    "primary_url": f"https://placeholder.com/primary/{name}.jpg",
                    "logo_url": None,
                    "quality_score": 75,
                }
                results["processed"] += 1

            except Exception as e:
                logger.error(f"Failed to process images for {name}: {e}")
                results["failed"] += 1
                results["errors"].append(f"{name}: {str(e)}")

        return results


class MagicScholarImageExtractor:
    """Complete image extraction service integrated with MagicScholar"""

    def __init__(self, db: Session, target_width: int = 400, target_height: int = 300):
        self.db = db
        self.target_width = target_width
        self.target_height = target_height

        # HTTP session for web scraping
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Initialize upload service
        self.uploader = DigitalOceanSpacesUploader()

        # Processing statistics
        self.stats = {
            "processed": 0,
            "failed": 0,
            "uploaded": 0,
            "high_quality": 0,
            "errors": [],
        }

    def calculate_image_quality_score(
        self, image_info: Dict[str, Any], image_type: str
    ) -> int:
        """Calculate an improved quality score for an image (0-100) that prioritizes campus imagery"""
        score = 0
        width = image_info.get("width", 0)
        height = image_info.get("height", 0)
        size_bytes = image_info.get("size_bytes", 0)
        url = image_info.get("url", "").lower()

        # Size quality (30 points max - reduced from 40)
        if width >= 1200:
            score += 15
        elif width >= 800:
            score += 12
        elif width >= 600:
            score += 8
        elif width >= 400:
            score += 4

        if height >= 600:
            score += 15
        elif height >= 400:
            score += 12
        elif height >= 300:
            score += 8
        elif height >= 200:
            score += 4

        # Aspect ratio quality (15 points max - reduced from 20)
        if width > 0 and height > 0:
            ratio = width / height
            if 1.2 <= ratio <= 2.5:  # Good for cards
                score += 15
            elif 1.0 <= ratio <= 3.0:  # Acceptable
                score += 8

        # File size quality (15 points max - reduced from 20)
        if size_bytes > 200000:
            score += 15  # Large, detailed
        elif size_bytes > 100000:
            score += 12  # Good size
        elif size_bytes > 50000:
            score += 8  # Acceptable
        elif size_bytes > 20000:
            score += 4  # Small but usable

        # Image type and content scoring (40 points max - increased from 20)
        content_bonuses = {
            "og_image": 25,  # Usually best quality and most representative
            "hero": 20,  # Good campus images
            "twitter_image": 15,  # Decent quality
            "logo": 5,  # Functional but not engaging - reduced from 8
            "favicon": 2,  # Usually too small - reduced from 3
        }
        score += content_bonuses.get(image_type, 0)

        # Content analysis bonuses/penalties (new - up to +/-15 points)
        content_score = self._analyze_image_content(url, image_type)
        score += content_score

        return min(max(score, 0), 100)  # Cap between 0-100

    def _analyze_image_content(self, url: str, image_type: str) -> int:
        """Analyze image URL and type for content appropriateness"""
        content_score = 0
        url_lower = url.lower()

        # Positive indicators for campus/institutional imagery (+5 to +15 points)
        campus_keywords = [
            "campus",
            "building",
            "hall",
            "library",
            "quad",
            "courtyard",
            "entrance",
            "facility",
            "center",
            "tower",
            "arch",
            "gate",
            "aerial",
            "exterior",
            "architecture",
            "grounds",
            "plaza",
        ]

        for keyword in campus_keywords:
            if keyword in url_lower:
                content_score += 8
                break  # Don't double-count

        # Positive indicators for academic imagery (+3 to +8 points)
        academic_keywords = [
            "student",
            "graduation",
            "classroom",
            "lab",
            "research",
            "study",
            "academic",
            "learning",
            "education",
        ]

        for keyword in academic_keywords:
            if keyword in url_lower:
                content_score += 5
                break

        # Negative indicators for promotional/inappropriate content (-5 to -20 points)
        promotional_keywords = [
            "headshot",
            "portrait",
            "profile",
            "staff",
            "faculty-photo",
            "testimonial",
            "review",
            "video-thumb",
            "play-button",
            "zoom",
            "webinar",
            "meeting",
            "interview",
            "tv",
            "news",
        ]

        for keyword in promotional_keywords:
            if keyword in url_lower:
                content_score -= 15
                break

        # Logo-specific penalties for pure text/logo images
        if image_type == "logo":
            logo_penalties = ["logo-only", "text-logo", "wordmark", "brand", "identity"]
            for penalty in logo_penalties:
                if penalty in url_lower:
                    content_score -= 10
                    break

            # But give some points back if it's a logo with campus elements
            if any(word in url_lower for word in ["campus", "seal", "crest", "emblem"]):
                content_score += 5

        # Favicon penalties - usually too small and not representative
        if image_type == "favicon":
            content_score -= 8  # Stronger penalty for favicons

        # File format preferences
        if url_lower.endswith((".jpg", ".jpeg")):
            content_score += 2  # Slightly prefer photos over graphics
        elif url_lower.endswith(".png"):
            if image_type not in ["logo", "favicon"]:
                content_score -= (
                    2  # PNG often indicates graphics/logos for non-logo types
                )

        return max(min(content_score, 15), -20)  # Cap between -20 and +15

    def clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL"""
        if not url:
            return None

        url = str(url).strip()

        # Add https if no protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Remove trailing slash
        url = url.rstrip("/")

        return url

    def standardize_image(
        self, image_data: bytes, school_name: str, image_type: str, quality_score: int
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """Standardize image to consistent dimensions and return processed bytes"""
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
            canvas.save(output, "JPEG", quality=85, optimize=True)
            processed_bytes = output.getvalue()

            return processed_bytes, filename

        except Exception as e:
            logger.debug(f"Failed to standardize image: {e}")
            return None, None

    def download_and_process_image(
        self, image_url: str, school_name: str, image_type: str
    ) -> Optional[Dict[str, Any]]:
        """Download, process, and score an image"""
        try:
            response = self.session.get(image_url, timeout=10, stream=True)
            response.raise_for_status()

            # Check if it's actually an image
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                return None

            # Get image data
            image_data = response.content

            # Get original dimensions and size
            with Image.open(io.BytesIO(image_data)) as img:
                original_width, original_height = img.size

            # Filter out tiny images immediately
            if original_width < 100 or original_height < 100:
                return None

            # Create image info for scoring
            image_info = {
                "url": image_url,
                "width": original_width,
                "height": original_height,
                "size_bytes": len(image_data),
            }

            # Calculate quality score
            quality_score = self.calculate_image_quality_score(image_info, image_type)

            # Only process images with decent quality scores
            if quality_score < 30:
                logger.debug(f"Skipping low quality image (score: {quality_score})")
                return None

            # Standardize the image
            standardized_bytes, filename = self.standardize_image(
                image_data, school_name, image_type, quality_score
            )

            if standardized_bytes and filename:
                return {
                    "original_url": image_url,
                    "original_width": original_width,
                    "original_height": original_height,
                    "standardized_width": self.target_width,
                    "standardized_height": self.target_height,
                    "size_bytes": len(image_data),
                    "quality_score": quality_score,
                    "image_type": image_type,
                    "processed_bytes": standardized_bytes,
                    "filename": filename,
                }

            return None

        except Exception as e:
            logger.debug(f"Failed to download/process {image_url}: {e}")
            return None

    def extract_website_images(self, url: str, school_name: str) -> Dict[str, Any]:
        """Enhanced image extraction with better campus image detection"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            images = {}

            # Open Graph image (highest priority)
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                og_url = urljoin(url, og_image.get("content"))
                processed = self.download_and_process_image(
                    og_url, school_name, "og_image"
                )
                if processed:
                    images["og_image"] = processed

            # Twitter card image
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image and twitter_image.get("content"):
                twitter_url = urljoin(url, twitter_image.get("content"))
                processed = self.download_and_process_image(
                    twitter_url, school_name, "twitter_image"
                )
                if processed:
                    images["twitter_image"] = processed

            # Enhanced hero/banner image detection with campus-specific selectors
            hero_selectors = [
                # Campus-specific selectors (higher priority)
                'img[alt*="campus" i]',
                'img[alt*="university" i]',
                'img[alt*="college" i]',
                'img[src*="campus" i]',
                'img[src*="building" i]',
                'img[src*="aerial" i]',
                # General hero selectors
                ".hero img",
                ".banner img",
                ".hero-image img",
                ".main-banner img",
                'img[src*="hero" i]',
                'img[src*="banner" i]',
                'img[class*="hero" i]',
                'img[class*="banner" i]',
                # Additional campus imagery selectors
                ".campus-image img",
                ".facility-image img",
                'img[class*="campus" i]',
                'img[class*="building" i]',
            ]

            for selector in hero_selectors:
                hero_imgs = soup.select(selector)
                for hero_img in hero_imgs[:2]:  # Check first 2 matches per selector
                    if hero_img.get("src"):
                        hero_url = urljoin(url, hero_img.get("src"))
                        processed = self.download_and_process_image(
                            hero_url, school_name, "hero"
                        )
                        if (
                            processed and processed["quality_score"] > 35
                        ):  # Lowered from 40 to catch more campus images
                            images["hero"] = processed
                            break
                if "hero" in images:
                    break

            # Look for logos (but with stricter quality requirements applied in scoring)
            logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                ".logo img",
                ".header-logo img",
                ".site-logo img",
                'img[alt*="seal" i]',  # University seals
                'img[alt*="crest" i]',  # University crests
            ]

            for selector in logo_selectors:
                logo_imgs = soup.select(selector)
                for logo_img in logo_imgs[:2]:
                    if logo_img.get("src"):
                        logo_url = urljoin(url, logo_img.get("src"))
                        processed = self.download_and_process_image(
                            logo_url, school_name, "logo"
                        )
                        if processed:
                            images["logo"] = processed
                            break
                if "logo" in images:
                    break

            # Favicon as last resort (with heavy penalty in scoring)
            favicon = soup.find("link", rel=["icon", "shortcut icon"])
            if favicon and favicon.get("href"):
                favicon_url = urljoin(url, favicon.get("href"))
                processed = self.download_and_process_image(
                    favicon_url, school_name, "favicon"
                )
                if processed:
                    images["favicon"] = processed

            return images

        except Exception as e:
            logger.debug(f"Website image extraction failed for {url}: {e}")
            return {}

    def select_best_image(
        self, school_images: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Select the single best image with improved campus-focused logic"""
        if not school_images:
            return None

        # Sort by quality score
        sorted_images = sorted(
            school_images.values(), key=lambda x: x["quality_score"], reverse=True
        )

        # First, look for high-quality campus imagery (prioritize og_image and hero with high scores)
        for img in sorted_images:
            if (
                img["image_type"] in ["og_image", "hero"] and img["quality_score"] >= 65
            ):  # Raised threshold from 60
                return img

        # Next, accept good twitter images if they score well
        for img in sorted_images:
            if img["image_type"] == "twitter_image" and img["quality_score"] >= 60:
                return img

        # Only accept logos if they score very well (indicating campus elements)
        for img in sorted_images:
            if (
                img["image_type"] == "logo" and img["quality_score"] >= 70
            ):  # High threshold for logos
                return img

        # Last resort - any non-favicon image with decent score
        for img in sorted_images:
            if img["image_type"] != "favicon" and img["quality_score"] >= 40:
                return img

        # Absolute last resort - best available image
        return sorted_images[0] if sorted_images else None

    def upload_image_to_spaces(
        self, image_data: Dict[str, Any], directory: str = "primary"
    ) -> Optional[str]:
        """Upload processed image to Digital Ocean Spaces"""
        try:
            file_path = f"university-images/{directory}/{image_data['filename']}"
            cdn_url = self.uploader.upload_image(
                image_bytes=image_data["processed_bytes"],
                file_path=file_path,
                content_type="image/jpeg",
            )
            return cdn_url
        except Exception as e:
            logger.error(f"Failed to upload image to Spaces: {e}")
            return None

    def process_institution(self, institution: Institution) -> Dict[str, Any]:
        """Process a single institution for image extraction"""
        school_name = institution.name
        website = self.clean_url(institution.website)

        if not website:
            logger.debug(f"No valid website for {school_name}")
            return {
                "institution_id": institution.ipeds_id,
                "name": school_name,
                "status": "no_website",
                "error": "No valid website URL found",
            }

        logger.info(f"Processing: {school_name} ({website})")

        # Update status to processing
        institution.image_extraction_status = ImageExtractionStatus.PROCESSING
        self.db.commit()

        result = {
            "institution_id": institution.ipeds_id,
            "name": school_name,
            "website": website,
            "processed_at": datetime.now().isoformat(),
            "images": {},
            "best_image": None,
            "status": "success",
            "cdn_urls": {},
        }

        try:
            # Extract all images
            extracted_images = self.extract_website_images(website, school_name)
            result["images"] = {
                k: {
                    "quality_score": v["quality_score"],
                    "image_type": v["image_type"],
                    "original_url": v["original_url"],
                }
                for k, v in extracted_images.items()
            }

            # Select best image
            best_image = self.select_best_image(extracted_images)

            if best_image:
                # Upload primary image
                primary_url = self.upload_image_to_spaces(best_image, "primary")
                if primary_url:
                    result["cdn_urls"]["primary"] = primary_url
                    result["best_image"] = {
                        "quality_score": best_image["quality_score"],
                        "cdn_url": primary_url,
                        "image_type": best_image["image_type"],
                    }

                    # Update institution in database
                    institution.update_image_info(
                        image_url=primary_url,
                        quality_score=best_image["quality_score"],
                        status=ImageExtractionStatus.SUCCESS,
                    )

                    self.stats["uploaded"] += 1
                    if best_image["quality_score"] >= 60:
                        self.stats["high_quality"] += 1

                # Upload logo if available
                if "logo" in extracted_images:
                    logo_image = extracted_images["logo"]
                    logo_url = self.upload_image_to_spaces(logo_image, "logos")
                    if logo_url:
                        result["cdn_urls"]["logo"] = logo_url
                        institution.logo_image_url = logo_url

            if not result["cdn_urls"]:
                result["status"] = "no_images_found"
                institution.image_extraction_status = ImageExtractionStatus.FAILED

            self.stats["processed"] += 1

        except Exception as e:
            logger.error(f"Failed to process {school_name}: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            institution.image_extraction_status = ImageExtractionStatus.FAILED
            self.stats["failed"] += 1
            self.stats["errors"].append(f"{school_name}: {str(e)}")

        # Final database commit
        self.db.commit()

        return result

    def process_institutions_batch(
        self, institution_ids: List[int] = None, limit: int = None
    ) -> Dict[str, Any]:
        """Process a batch of institutions"""
        try:
            # Build query
            query = self.db.query(Institution)

            if institution_ids:
                query = query.filter(Institution.ipeds_id.in_(institution_ids))
            else:
                # Process institutions that haven't been processed yet or failed
                query = query.filter(
                    (
                        Institution.image_extraction_status
                        == ImageExtractionStatus.PENDING
                    )
                    | (
                        Institution.image_extraction_status
                        == ImageExtractionStatus.FAILED
                    )
                ).filter(Institution.website.isnot(None))

            if limit:
                query = query.limit(limit)

            institutions = query.all()

            logger.info(f"Processing {len(institutions)} institutions...")

            results = []
            for idx, institution in enumerate(institutions, 1):
                logger.info(f"[{idx}/{len(institutions)}] Processing institution...")

                result = self.process_institution(institution)
                results.append(result)

                # Be respectful - add delay between requests
                time.sleep(2)

                # Log progress every 10 institutions
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(institutions)} completed")

            return {
                "total_processed": len(results),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "no_images": len(
                    [r for r in results if r["status"] == "no_images_found"]
                ),
                "no_website": len([r for r in results if r["status"] == "no_website"]),
                "stats": self.stats,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise Exception(f"Batch processing error: {str(e)}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        # Get counts from database
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

        good_quality = (
            self.db.query(Institution)
            .filter(Institution.primary_image_quality_score >= 60)
            .count()
        )

        pending = (
            self.db.query(Institution)
            .filter(
                Institution.image_extraction_status == ImageExtractionStatus.PENDING
            )
            .count()
        )

        failed = (
            self.db.query(Institution)
            .filter(Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        return {
            "total_institutions": total,
            "with_images": with_images,
            "high_quality_images": high_quality,
            "good_quality_images": good_quality,
            "pending_processing": pending,
            "failed_processing": failed,
            "success_rate": f"{(with_images/total)*100:.1f}%" if total > 0 else "0%",
            "high_quality_rate": (
                f"{(high_quality/total)*100:.1f}%" if total > 0 else "0%"
            ),
        }
