# app/services/image_extractor.py
"""
Enhanced University Image Extractor for MagicScholar
Extracts images from university websites and integrates with upload service
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from pathlib import Path
import logging
import time
import json
from PIL import Image
import io
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.institution import Institution, ImageExtractionStatus


logger = logging.getLogger(__name__)


class ImageUploadService:
    """Temporary placeholder upload service"""

    def __init__(self, db: Session):
        self.db = db

    def process_institution_images(self, batch_data):
        """Placeholder - simulates upload without actually uploading"""
        results = {"processed": 0, "failed": 0, "uploaded_urls": {}, "errors": []}

        for item in batch_data:
            ipeds_id = item.get("ipeds_id")
            name = item.get("name", "Unknown")

            # Simulate successful upload
            results["uploaded_urls"][ipeds_id] = {
                "primary_url": f"https://placeholder.com/primary/{name}.jpg",
                "logo_url": None,
                "quality_score": 75,
            }
            results["processed"] += 1

        return results


class MagicScholarImageExtractor:
    """Image extractor integrated with MagicScholar's database and upload service"""

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
        self.upload_service = ImageUploadService(db)

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
        """Calculate a quality score for an image (0-100)"""
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

    def clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL"""
        if not url or pd.isna(url):
            return None

        url = str(url).strip()

        # Add https if no protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Remove trailing slash
        url = url.rstrip("/")

        return url

    def download_and_process_image(
        self, image_url: str, school_name: str, image_type: str
    ) -> Optional[Dict[str, Any]]:
        """Download, process, and score an image - returns data in memory"""
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

            # Return image data in memory (no file saving)
            return {
                "url": image_url,
                "data": image_data,  # Raw image data
                "original_width": original_width,
                "original_height": original_height,
                "size_bytes": len(image_data),
                "quality_score": quality_score,
                "image_type": image_type,
            }

        except Exception as e:
            logger.debug(f"Failed to download/process {image_url}: {e}")
            return None

    def extract_website_images(self, url: str, school_name: str) -> Dict[str, Any]:
        """Extract all possible images from a website"""
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

            # Look for hero/banner images
            hero_selectors = [
                ".hero img",
                ".banner img",
                ".hero-image img",
                ".main-banner img",
                'img[alt*="campus" i]',
                'img[alt*="university" i]',
                'img[src*="hero" i]',
                'img[src*="banner" i]',
                'img[class*="hero" i]',
                'img[class*="banner" i]',
            ]

            for selector in hero_selectors:
                hero_imgs = soup.select(selector)
                for hero_img in hero_imgs[:3]:  # Check first 3 matches
                    if hero_img.get("src"):
                        hero_url = urljoin(url, hero_img.get("src"))
                        processed = self.download_and_process_image(
                            hero_url, school_name, "hero"
                        )
                        if (
                            processed and processed["quality_score"] > 40
                        ):  # Only good hero images
                            images["hero"] = processed
                            break
                if "hero" in images:
                    break

            # Look for logos
            logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                ".logo img",
                ".header-logo img",
                ".site-logo img",
            ]

            for selector in logo_selectors:
                logo_imgs = soup.select(selector)
                for logo_img in logo_imgs[:2]:  # Check first 2 matches
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

            # Favicon as last resort
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
        """Select the single best image for the school card"""
        if not school_images:
            return None

        # Sort by quality score
        sorted_images = sorted(
            school_images.values(), key=lambda x: x["quality_score"], reverse=True
        )

        # Prefer certain types with high scores
        for img in sorted_images:
            if img["image_type"] in ["og_image", "hero"] and img["quality_score"] >= 60:
                return img

        # Fall back to best scoring image of any type (except favicon unless it's really good)
        for img in sorted_images:
            if img["image_type"] != "favicon" or img["quality_score"] >= 70:
                return img

        # Last resort - any image
        return sorted_images[0] if sorted_images else None

    def process_institution_from_db(self, institution: Institution) -> Dict[str, Any]:
        """Process a single institution from the database"""
        school_name = institution.name
        website = self.clean_url(institution.website)

        result = {
            "institution_id": institution.id,
            "ipeds_id": institution.ipeds_id,
            "name": school_name,
            "website": website,
            "status": "success",
            "images": {},
            "best_image": None,
            "uploaded_urls": {},
        }

        if not website:
            logger.debug(f"No valid website for {school_name}")
            result["status"] = "no_website"
            return result

        logger.info(f"Processing: {school_name} ({website})")

        try:
            # Extract all images from website
            extracted_images = self.extract_website_images(website, school_name)
            result["images"] = extracted_images

            # Select best image
            best_image = self.select_best_image(extracted_images)
            result["best_image"] = best_image

            if best_image:
                # Prepare data for upload service
                batch_data = [
                    {
                        "ipeds_id": institution.ipeds_id,
                        "name": school_name,
                        "images": {
                            "primary": {
                                "data": best_image["data"],
                                "type": best_image["image_type"],
                                "width": best_image["original_width"],
                                "height": best_image["original_height"],
                                "size_bytes": best_image["size_bytes"],
                            }
                        },
                    }
                ]

                # Add logo if available
                if "logo" in extracted_images:
                    logo_image = extracted_images["logo"]
                    batch_data[0]["images"]["logo"] = {
                        "data": logo_image["data"],
                        "type": "logo",
                        "width": logo_image["original_width"],
                        "height": logo_image["original_height"],
                        "size_bytes": logo_image["size_bytes"],
                    }

                # Upload to Digital Ocean
                upload_results = self.upload_service.process_institution_images(
                    batch_data
                )

                if upload_results["processed"] > 0:
                    result["uploaded_urls"] = upload_results["uploaded_urls"]
                    result["status"] = "uploaded"
                    self.stats["uploaded"] += 1

                    if best_image["quality_score"] >= 80:
                        self.stats["high_quality"] += 1
                else:
                    result["status"] = "upload_failed"
                    result["errors"] = upload_results["errors"]

            image_count = len(extracted_images)
            best_score = best_image["quality_score"] if best_image else 0
            logger.info(f"  → Extracted {image_count} images, best score: {best_score}")

            if image_count == 0:
                result["status"] = "no_images_found"

            self.stats["processed"] += 1

        except Exception as e:
            logger.error(f"  → Failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            self.stats["failed"] += 1
            self.stats["errors"].append(f"{school_name}: {str(e)}")

        return result

    def process_institutions_from_csv(
        self, csv_path: str, max_institutions: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Process institutions from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} institutions from CSV")

            if max_institutions:
                df = df.head(max_institutions)
                logger.info(f"Limited to {max_institutions} institutions for testing")

            results = []

            for idx, (_, row) in enumerate(df.iterrows(), 1):
                school_name = row["name"]
                website = self.clean_url(row["website"])
                ipeds_id = row["ipeds_id"]

                # Find institution in database
                institution = (
                    self.db.query(Institution)
                    .filter(Institution.ipeds_id == ipeds_id)
                    .first()
                )

                if not institution:
                    logger.warning(
                        f"Institution not found in database: {school_name} (IPEDS ID: {ipeds_id})"
                    )
                    continue

                logger.info(f"[{idx}/{len(df)}] Processing {school_name}...")

                result = self.process_institution_from_db(institution)
                results.append(result)

                # Be respectful - add delay between requests
                time.sleep(1)

            return results

        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            raise

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        total_attempts = self.stats["processed"] + self.stats["failed"]

        return {
            "processed": self.stats["processed"],
            "failed": self.stats["failed"],
            "uploaded": self.stats["uploaded"],
            "high_quality": self.stats["high_quality"],
            "success_rate": (
                (self.stats["processed"] / total_attempts * 100)
                if total_attempts > 0
                else 0
            ),
            "upload_rate": (
                (self.stats["uploaded"] / self.stats["processed"] * 100)
                if self.stats["processed"] > 0
                else 0
            ),
            "high_quality_rate": (
                (self.stats["high_quality"] / self.stats["uploaded"] * 100)
                if self.stats["uploaded"] > 0
                else 0
            ),
            "errors": self.stats["errors"][-10:],  # Last 10 errors
        }
