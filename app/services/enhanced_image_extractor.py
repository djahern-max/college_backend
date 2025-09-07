# app/services/enhanced_image_extractor.py
"""
Enhanced University Image Extraction Service for MagicScholar
Includes improved image extraction logic and Digital Ocean Spaces deletion capabilities
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import time
import hashlib
from PIL import Image
import io
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import os
import re

from app.models.institution import Institution, ImageExtractionStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedDigitalOceanSpacesManager:
    """Enhanced manager for Digital Ocean Spaces with deletion capabilities"""

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

    def delete_existing_images(self, institution_name: str) -> bool:
        """Delete existing images for an institution from Digital Ocean Spaces"""
        try:
            # Create safe filename prefix for this institution
            safe_name = self._create_safe_filename(institution_name)

            # List all objects with this institution's prefix
            prefixes = [
                f"university-images/primary/{safe_name}",
                f"university-images/logos/{safe_name}",
            ]

            deleted_count = 0
            for prefix in prefixes:
                try:
                    # List objects with this prefix
                    response = self.spaces_client.list_objects_v2(
                        Bucket=self.bucket_name, Prefix=prefix
                    )

                    if "Contents" in response:
                        # Delete each object
                        for obj in response["Contents"]:
                            self.spaces_client.delete_object(
                                Bucket=self.bucket_name, Key=obj["Key"]
                            )
                            deleted_count += 1
                            logger.info(f"Deleted existing image: {obj['Key']}")

                except ClientError as e:
                    logger.warning(
                        f"Could not list/delete objects with prefix {prefix}: {e}"
                    )

            if deleted_count > 0:
                logger.info(
                    f"Deleted {deleted_count} existing images for {institution_name}"
                )
            return True

        except Exception as e:
            logger.error(
                f"Failed to delete existing images for {institution_name}: {e}"
            )
            return False

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
                ACL="public-read",
                CacheControl="max-age=31536000",  # Cache for 1 year
            )

            # Return CDN URL
            cdn_url = f"{self.cdn_endpoint}/{file_path}"
            logger.info(f"Successfully uploaded image to: {cdn_url}")
            return cdn_url

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to upload image to Spaces: {e}")
            return None

    def _create_safe_filename(self, institution_name: str) -> str:
        """Create a safe filename from institution name"""
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r"[^\w\s-]", "", institution_name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name)
        return safe_name[:50]  # Limit length


class EnhancedImageExtractor:
    """Enhanced image extraction service with improved OG image detection"""

    def __init__(self, db: Session):
        self.db = db
        self.spaces_manager = EnhancedDigitalOceanSpacesManager()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.target_width = 400
        self.target_height = 300

        # Statistics tracking
        self.stats = {
            "processed": 0,
            "uploaded": 0,
            "high_quality": 0,
            "failed": 0,
            "errors": [],
        }

    def extract_enhanced_website_images(
        self, url: str, school_name: str
    ) -> Dict[str, Any]:
        """Enhanced image extraction prioritizing OG images and campus imagery"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            images = {}

            # Priority 1: Open Graph images (often the best quality campus images)
            og_selectors = [
                ('meta[property="og:image"]', "content"),
                ('meta[property="og:image:url"]', "content"),
                ('meta[name="og:image"]', "content"),
            ]

            for selector, attr in og_selectors:
                og_tags = soup.select(selector)
                for og_tag in og_tags[:2]:  # Check first 2 OG images
                    if og_tag.get(attr):
                        og_url = urljoin(url, og_tag.get(attr))
                        processed = self.download_and_process_image(
                            og_url, school_name, "og_image"
                        )
                        if processed and processed["quality_score"] > 50:
                            images["og_image"] = processed
                            break
                if "og_image" in images:
                    break

            # Priority 2: Twitter Card images (usually high quality)
            twitter_selectors = [
                ('meta[name="twitter:image"]', "content"),
                ('meta[name="twitter:image:src"]', "content"),
                ('meta[property="twitter:image"]', "content"),
            ]

            for selector, attr in twitter_selectors:
                twitter_tags = soup.select(selector)
                for twitter_tag in twitter_tags[:2]:
                    if twitter_tag.get(attr):
                        twitter_url = urljoin(url, twitter_tag.get(attr))
                        processed = self.download_and_process_image(
                            twitter_url, school_name, "twitter_image"
                        )
                        if processed and processed["quality_score"] > 45:
                            images["twitter_image"] = processed
                            break
                if "twitter_image" in images:
                    break

            # Priority 3: Enhanced campus-specific hero/banner images
            campus_hero_selectors = [
                # Campus-specific alt text
                'img[alt*="campus" i]',
                'img[alt*="university" i]',
                'img[alt*="college" i]',
                'img[alt*="aerial" i]',
                'img[alt*="view" i]',
                'img[alt*="building" i]',
                # Campus-specific src paths
                'img[src*="campus" i]',
                'img[src*="aerial" i]',
                'img[src*="university" i]',
                'img[src*="building" i]',
                'img[src*="quad" i]',
                # Hero/banner selectors
                ".hero img",
                ".banner img",
                ".hero-image img",
                ".main-banner img",
                ".campus-image img",
                ".facility-image img",
                # Class-based campus selectors
                'img[class*="campus" i]',
                'img[class*="hero" i]',
                'img[class*="banner" i]',
                'img[class*="main" i]',
            ]

            for selector in campus_hero_selectors:
                hero_imgs = soup.select(selector)
                for hero_img in hero_imgs[:3]:  # Check first 3 matches per selector
                    if hero_img.get("src"):
                        hero_url = urljoin(url, hero_img.get("src"))
                        processed = self.download_and_process_image(
                            hero_url, school_name, "hero"
                        )
                        if processed and processed["quality_score"] > 35:
                            images["hero"] = processed
                            break
                if "hero" in images:
                    break

            # Priority 4: Logo images (with stricter requirements)
            logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                ".logo img",
                ".header-logo img",
                ".site-logo img",
                'img[alt*="seal" i]',
                'img[alt*="crest" i]',
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

            # Priority 5: Favicon as absolute last resort
            favicon_selectors = [
                'link[rel="icon"]',
                'link[rel="shortcut icon"]',
                'link[rel="apple-touch-icon"]',
            ]

            for selector in favicon_selectors:
                favicons = soup.select(selector)
                for favicon in favicons:
                    if favicon.get("href"):
                        favicon_url = urljoin(url, favicon.get("href"))
                        processed = self.download_and_process_image(
                            favicon_url, school_name, "favicon"
                        )
                        if processed:
                            images["favicon"] = processed
                            break
                if "favicon" in images:
                    break

            return images

        except Exception as e:
            logger.debug(f"Enhanced image extraction failed for {url}: {e}")
            return {}

    def download_and_process_image(
        self, image_url: str, school_name: str, image_type: str
    ) -> Optional[Dict[str, Any]]:
        """Download and process a single image with enhanced quality scoring"""
        try:
            response = self.session.get(image_url, timeout=10, stream=True)
            response.raise_for_status()

            # Validate content type
            content_type = response.headers.get("content-type", "").lower()
            if not any(
                img_type in content_type
                for img_type in ["image/jpeg", "image/png", "image/webp"]
            ):
                return None

            image_data = response.content
            if len(image_data) < 1024:  # Too small
                return None

            # Process image
            img = Image.open(io.BytesIO(image_data))
            original_width, original_height = img.size

            # Enhanced quality scoring
            image_info = {
                "url": image_url,
                "width": original_width,
                "height": original_height,
                "size_bytes": len(image_data),
                "image_type": image_type,
            }

            quality_score = self.calculate_enhanced_quality_score(
                image_info, school_name
            )

            # Skip very low quality images
            if quality_score < 25:
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

    def calculate_enhanced_quality_score(
        self, image_info: Dict[str, Any], school_name: str
    ) -> float:
        """Enhanced quality scoring that prioritizes campus imagery"""
        score = 0.0
        width = image_info["width"]
        height = image_info["height"]
        url = image_info["url"].lower()
        image_type = image_info["image_type"]

        # Base score from dimensions (0-40 points)
        if width >= 800 and height >= 600:
            score += 40
        elif width >= 600 and height >= 400:
            score += 30
        elif width >= 400 and height >= 300:
            score += 20
        elif width >= 200 and height >= 150:
            score += 10

        # Aspect ratio bonus (0-10 points)
        aspect_ratio = width / height if height > 0 else 0
        if 1.2 <= aspect_ratio <= 2.0:  # Good landscape ratio
            score += 10
        elif 0.8 <= aspect_ratio <= 1.2:  # Square-ish (good for logos)
            score += 5

        # Image type bonuses
        if image_type == "og_image":
            score += 25  # OG images are usually the best
        elif image_type == "twitter_image":
            score += 20  # Twitter images are usually high quality
        elif image_type == "hero":
            score += 15  # Hero images are good
        elif image_type == "logo":
            score += 5  # Logos are OK but not preferred
        elif image_type == "favicon":
            score -= 10  # Penalize favicons

        # URL content analysis (0-15 points)
        campus_keywords = [
            "campus",
            "aerial",
            "university",
            "college",
            "building",
            "quad",
            "main",
        ]
        quality_keywords = ["hero", "banner", "main", "primary", "featured"]

        url_bonus = 0
        for keyword in campus_keywords:
            if keyword in url:
                url_bonus += 3
        for keyword in quality_keywords:
            if keyword in url:
                url_bonus += 2

        score += min(url_bonus, 15)

        # File size consideration (0-10 points)
        size_mb = image_info["size_bytes"] / (1024 * 1024)
        if 0.5 <= size_mb <= 5.0:  # Good file size range
            score += 10
        elif 0.1 <= size_mb <= 10.0:  # Acceptable range
            score += 5

        # Penalties
        if width < 200 or height < 150:
            score -= 20  # Too small
        if "favicon" in url or "icon" in url:
            score -= 15  # Likely favicon
        if size_mb > 10:
            score -= 10  # Too large

        return max(0, min(100, score))

    def standardize_image(
        self, image_data: bytes, school_name: str, image_type: str, quality_score: int
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """Standardize image to consistent dimensions"""
        try:
            img = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background

            # Resize to target dimensions
            img = img.resize(
                (self.target_width, self.target_height), Image.Resampling.LANCZOS
            )

            # Create filename
            safe_name = re.sub(r"[^\w\s-]", "", school_name)
            safe_name = re.sub(r"[-\s]+", "_", safe_name)[:50]
            filename = f"{safe_name}_q{quality_score}_{image_type}.jpg"

            # Save as JPEG
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)

            return output.getvalue(), filename

        except Exception as e:
            logger.error(f"Failed to standardize image: {e}")
            return None, None

    def select_best_image(self, images: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Select the best image using enhanced prioritization"""
        if not images:
            return None

        # Sort by quality score
        sorted_images = sorted(
            images.values(), key=lambda x: x["quality_score"], reverse=True
        )

        # Prioritize by type and score
        priorities = [
            ("og_image", 60),  # High-quality OG images
            ("twitter_image", 55),  # High-quality Twitter images
            ("hero", 50),  # High-quality hero images
            ("og_image", 40),  # Lower quality OG images
            ("twitter_image", 40),  # Lower quality Twitter images
            ("hero", 35),  # Lower quality hero images
            ("logo", 65),  # Only very high-quality logos
            ("favicon", 50),  # Only if very high quality
        ]

        for img_type, min_score in priorities:
            for img in sorted_images:
                if img["image_type"] == img_type and img["quality_score"] >= min_score:
                    return img

        # Fallback to highest scoring image
        return sorted_images[0] if sorted_images else None

    def process_institution(self, institution: Institution) -> Dict[str, Any]:
        """Process a single institution with enhanced extraction and deletion"""
        school_name = institution.name
        website = self.clean_url(institution.website)

        if not website:
            return {
                "institution_id": institution.ipeds_id,
                "name": school_name,
                "status": "no_website",
                "error": "No valid website URL found",
            }

        logger.info(f"Processing: {school_name} ({website})")

        # Delete existing images first
        self.spaces_manager.delete_existing_images(school_name)

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
            # Extract images using enhanced method
            extracted_images = self.extract_enhanced_website_images(
                website, school_name
            )
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
                    institution.primary_image_url = primary_url
                    institution.primary_image_quality_score = best_image[
                        "quality_score"
                    ]
                    institution.image_extraction_status = ImageExtractionStatus.SUCCESS
                    institution.image_extraction_date = datetime.now()

                    self.stats["uploaded"] += 1
                    if best_image["quality_score"] >= 60:
                        self.stats["high_quality"] += 1

                # Upload logo if available and different from primary
                if (
                    "logo" in extracted_images
                    and extracted_images["logo"] != best_image
                ):
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

    def upload_image_to_spaces(
        self, image_data: Dict[str, Any], directory: str = "primary"
    ) -> Optional[str]:
        """Upload processed image to Digital Ocean Spaces"""
        try:
            file_path = f"university-images/{directory}/{image_data['filename']}"
            cdn_url = self.spaces_manager.upload_image(
                image_bytes=image_data["processed_bytes"],
                file_path=file_path,
                content_type="image/jpeg",
            )
            return cdn_url
        except Exception as e:
            logger.error(f"Failed to upload image to Spaces: {e}")
            return None

    def clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL"""
        if not url:
            return None

        url = str(url).strip()
        if not url or url.lower() in ["none", "null", "nan"]:
            return None

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    def process_institutions_batch(
        self, institution_ids: List[int] = None, limit: int = None
    ) -> Dict[str, Any]:
        """Process a batch of institutions using enhanced extraction"""
        try:
            # Build query for institutions from institutions_processed.csv
            query = self.db.query(Institution)

            if institution_ids:
                query = query.filter(Institution.ipeds_id.in_(institution_ids))
            else:
                query = query.filter(
                    (
                        Institution.image_extraction_status
                        == ImageExtractionStatus.PENDING
                    )
                    | (Institution.image_extraction_status.is_(None))
                ).filter(Institution.website.isnot(None))

            # Add this line before the limit:
            query = query.order_by(Institution.ipeds_id)

            if limit:
                query = query.limit(limit)

            institutions = query.all()
            logger.info(
                f"Processing {len(institutions)} institutions with enhanced extraction..."
            )

            results = []
            for idx, institution in enumerate(institutions, 1):
                logger.info(
                    f"[{idx}/{len(institutions)}] Processing {institution.name}"
                )
                result = self.process_institution(institution)
                results.append(result)

                # Brief pause to be respectful to servers
                if idx % 10 == 0:
                    time.sleep(1)

            return {
                "total_processed": len(results),
                "successful": self.stats["uploaded"],
                "failed": self.stats["failed"],
                "high_quality": self.stats["high_quality"],
                "stats": self.stats,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise
