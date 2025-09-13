# app/services/scholarship_image_extractor.py
"""
Scholarship Image Extractor Service
Inherits from the base image extractor and provides scholarship-specific functionality
"""

import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup
import re

from app.services.image_extractor import MagicScholarImageExtractor
from app.models.scholarship import Scholarship
from app.models.institution import ImageExtractionStatus

logger = logging.getLogger(__name__)


class ScholarshipImageExtractor(MagicScholarImageExtractor):
    """
    Scholarship-specific image extraction that inherits from the base extractor
    """

    def __init__(self, db: Session):
        super().__init__(db)
        self.stats.update(
            {
                "processed_scholarships": 0,
                "successful_scholarships": 0,
                "failed_scholarships": 0,
                "no_website_scholarships": 0,
                "org_logos_found": 0,
                "program_banners_found": 0,
            }
        )

    def _analyze_scholarship_content(
        self, url: str, image_type: str, organization: str
    ) -> int:
        """
        Analyze image URL and type for scholarship/organization appropriateness
        """
        content_score = 0
        url_lower = url.lower()
        org_lower = organization.lower()

        # Positive indicators for organization/scholarship imagery (+5 to +15 points)
        org_keywords = [
            "logo",
            "brand",
            "foundation",
            "scholarship",
            "award",
            "program",
            "organization",
            "institution",
            "fund",
            "grant",
            "education",
            "academic",
            "merit",
            "achievement",
            "excellence",
            "leadership",
        ]

        for keyword in org_keywords:
            if keyword in url_lower:
                content_score += 8
                break  # Don't double-count

        # Check if organization name appears in URL (+10 points)
        org_words = [word for word in org_lower.split() if len(word) > 3]
        for word in org_words:
            if word in url_lower:
                content_score += 10
                break

        # Positive indicators for educational/award imagery (+3 to +8 points)
        educational_keywords = [
            "student",
            "graduation",
            "graduate",
            "college",
            "university",
            "degree",
            "diploma",
            "ceremony",
            "academic",
            "learning",
            "scholar",
            "fellows",
            "winner",
            "recipient",
        ]

        for keyword in educational_keywords:
            if keyword in url_lower:
                content_score += 5
                break

        # Negative indicators for inappropriate content (-5 to -20 points)
        negative_keywords = [
            "staff",
            "employee",
            "board",
            "directors",
            "meeting",
            "office",
            "construction",
            "building",
            "facility",
            "news",
            "event",
            "conference",
            "generic",
            "stock",
            "placeholder",
            "temp",
        ]

        for keyword in negative_keywords:
            if keyword in url_lower:
                content_score -= 8
                break

        return max(-15, min(15, content_score))

    def _calculate_scholarship_quality_score(
        self,
        width: int,
        height: int,
        size_bytes: int,
        image_type: str,
        url: str,
        organization: str,
    ) -> int:
        """
        Calculate quality score specifically for scholarship images
        """
        score = 0

        # Dimension scoring (25 points max)
        if width > 0 and height > 0:
            ratio = width / height
            if 1.0 <= ratio <= 3.0:  # Good for organization logos and banners
                score += 25
            elif 0.5 <= ratio <= 4.0:  # Acceptable
                score += 15

        # Size scoring (15 points max)
        if size_bytes > 100000:  # 100KB+
            score += 15
        elif size_bytes > 50000:  # 50KB+
            score += 12
        elif size_bytes > 20000:  # 20KB+
            score += 8
        elif size_bytes > 10000:  # 10KB+
            score += 4

        # Image type scoring (40 points max)
        type_scores = {
            "og_image": 30,  # Usually best quality
            "twitter_image": 25,  # Good quality
            "org_logo": 35,  # Perfect for scholarships
            "hero": 20,  # Good organizational imagery
            "logo": 25,  # Organization branding
            "favicon": 5,  # Too small usually
        }
        score += type_scores.get(image_type, 10)

        # Content analysis (15 points max)
        content_score = self._analyze_scholarship_content(url, image_type, organization)
        score += content_score

        # Quality penalties
        penalties = [
            (width < 200 or height < 150, -15),  # Too small
            ("favicon" in url.lower(), -20),  # Likely favicon
            (size_bytes > 10 * 1024 * 1024, -10),  # Too large (>10MB)
            (ratio > 5.0 if width > 0 and height > 0 else False, -10),  # Too wide
        ]

        for condition, penalty in penalties:
            if condition:
                score += penalty

        return max(0, min(100, score))

    def extract_images_from_scholarship_website(
        self, url: str, organization: str
    ) -> Dict[str, Dict]:
        """
        Extract images from scholarship organization website
        """
        extracted_images = {}

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # 1. Extract Open Graph image (highest priority for orgs)
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                og_url = urljoin(url, og_image.get("content"))
                processed = self.download_and_process_scholarship_image(
                    og_url, organization, "og_image"
                )
                if processed and processed["quality_score"] > 30:
                    extracted_images["og_image"] = processed

            # 2. Extract Twitter image
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image and twitter_image.get("content"):
                twitter_url = urljoin(url, twitter_image.get("content"))
                processed = self.download_and_process_scholarship_image(
                    twitter_url, organization, "twitter_image"
                )
                if processed and processed["quality_score"] > 25:
                    extracted_images["twitter_image"] = processed

            # 3. Organization logo selectors
            org_logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                ".logo img",
                ".header-logo img",
                ".site-logo img",
                ".organization-logo img",
                ".foundation-logo img",
                'img[alt*="foundation" i]',
                'img[alt*="organization" i]',
            ]

            for selector in org_logo_selectors:
                logo_imgs = soup.select(selector)
                for logo_img in logo_imgs[:3]:  # Check first 3 matches
                    if logo_img.get("src"):
                        logo_url = urljoin(url, logo_img.get("src"))
                        processed = self.download_and_process_scholarship_image(
                            logo_url, organization, "org_logo"
                        )
                        if processed and processed["quality_score"] > 25:
                            if (
                                "org_logo" not in extracted_images
                                or processed["quality_score"]
                                > extracted_images["org_logo"]["quality_score"]
                            ):
                                extracted_images["org_logo"] = processed

            # 4. Hero/banner images (scholarship program imagery)
            hero_selectors = [
                ".hero img",
                ".banner img",
                ".main-banner img",
                'img[src*="hero" i]',
                'img[src*="banner" i]',
                'img[alt*="scholarship" i]',
                'img[alt*="program" i]',
                'img[alt*="award" i]',
                'img[class*="hero" i]',
                'img[class*="banner" i]',
                'img[class*="scholarship" i]',
                'img[class*="program" i]',
            ]

            for selector in hero_selectors:
                hero_imgs = soup.select(selector)
                for hero_img in hero_imgs[:2]:
                    if hero_img.get("src"):
                        hero_url = urljoin(url, hero_img.get("src"))
                        processed = self.download_and_process_scholarship_image(
                            hero_url, organization, "hero"
                        )
                        if processed and processed["quality_score"] > 20:
                            if (
                                "hero" not in extracted_images
                                or processed["quality_score"]
                                > extracted_images["hero"]["quality_score"]
                            ):
                                extracted_images["hero"] = processed

        except Exception as e:
            logger.error(f"Error extracting images from {url}: {e}")

        return extracted_images

    def download_and_process_scholarship_image(
        self, image_url: str, organization: str, image_type: str
    ) -> Optional[Dict]:
        """
        Download and process a scholarship image with organization-specific scoring
        """
        try:
            # Download image
            response = requests.get(image_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Get image info
            image_info = self.get_image_info(response.content)
            if not image_info:
                return None

            # Calculate quality score using scholarship-specific logic
            quality_score = self._calculate_scholarship_quality_score(
                image_info["width"],
                image_info["height"],
                image_info["size_bytes"],
                image_type,
                image_url,
                organization,
            )

            # Skip very low quality images
            if quality_score < 15:
                return None

            # Process image (resize, optimize)
            processed_image = self.process_image(response.content)
            if not processed_image:
                return None

            return {
                "image_data": processed_image,
                "original_url": image_url,
                "image_type": image_type,
                "quality_score": quality_score,
                "width": image_info["width"],
                "height": image_info["height"],
                "size_bytes": len(processed_image),
                "organization": organization,
            }

        except Exception as e:
            logger.error(f"Error processing scholarship image {image_url}: {e}")
            return None

    def process_scholarship(self, scholarship: Scholarship) -> Dict[str, Any]:
        """
        Process a single scholarship for image extraction
        """
        result = {
            "scholarship_id": scholarship.id,
            "title": scholarship.title,
            "organization": scholarship.organization,
            "status": "success",
            "cdn_urls": {},
            "best_image": None,
            "error": None,
        }

        try:
            logger.info(f"Processing scholarship: {scholarship.title}")

            # Skip if no website
            if not scholarship.website_url:
                result["status"] = "no_website"
                scholarship.image_extraction_status = ImageExtractionStatus.FAILED
                self.stats["no_website_scholarships"] += 1
                self.db.commit()
                return result

            # Extract images from website
            extracted_images = self.extract_images_from_scholarship_website(
                scholarship.website_url, scholarship.organization
            )

            if not extracted_images:
                result["status"] = "no_images_found"
                scholarship.image_extraction_status = ImageExtractionStatus.FAILED
                self.stats["failed_scholarships"] += 1
            else:
                # Find the best image
                best_image = max(
                    extracted_images.values(), key=lambda x: x["quality_score"]
                )

                result["best_image"] = best_image

                # Upload to CDN
                primary_url = self.upload_image_to_spaces(
                    best_image["image_data"],
                    f"scholarship-images/primary/{scholarship.id}",
                )

                if primary_url:
                    result["cdn_urls"]["primary"] = primary_url
                    scholarship.primary_image_url = primary_url
                    scholarship.primary_image_quality_score = best_image[
                        "quality_score"
                    ]
                    scholarship.image_extraction_status = ImageExtractionStatus.SUCCESS

                    # Upload logo separately if we found one
                    if (
                        "org_logo" in extracted_images
                        and extracted_images["org_logo"] != best_image
                    ):
                        logo_url = self.upload_image_to_spaces(
                            extracted_images["org_logo"]["image_data"],
                            f"scholarship-images/logos/{scholarship.id}",
                        )
                        if logo_url:
                            result["cdn_urls"]["logo"] = logo_url
                            scholarship.logo_image_url = logo_url
                            self.stats["org_logos_found"] += 1

                    self.stats["successful_scholarships"] += 1
                else:
                    result["status"] = "upload_failed"
                    scholarship.image_extraction_status = ImageExtractionStatus.FAILED
                    self.stats["failed_scholarships"] += 1

            self.stats["processed_scholarships"] += 1

            # Update extraction date
            from datetime import datetime

            scholarship.image_extraction_date = datetime.utcnow()

        except Exception as e:
            logger.error(f"Failed to process scholarship {scholarship.title}: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            scholarship.image_extraction_status = ImageExtractionStatus.FAILED
            self.stats["failed_scholarships"] += 1

        # Commit changes
        self.db.commit()
        return result

    def process_scholarships_batch(
        self,
        scholarship_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        force_reprocess: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a batch of scholarships for image extraction
        """
        try:
            # Build query
            query = self.db.query(Scholarship)

            if scholarship_ids:
                query = query.filter(Scholarship.id.in_(scholarship_ids))
            else:
                if force_reprocess:
                    # Process all scholarships with websites
                    query = query.filter(Scholarship.website_url.isnot(None))
                else:
                    # Only process scholarships that haven't been processed or failed
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

            scholarships = query.all()
            logger.info(
                f"Processing {len(scholarships)} scholarships for image extraction..."
            )

            results = []
            for idx, scholarship in enumerate(scholarships, 1):
                logger.info(
                    f"[{idx}/{len(scholarships)}] Processing {scholarship.title}"
                )
                result = self.process_scholarship(scholarship)
                results.append(result)

                # Brief pause between requests
                if idx % 5 == 0:
                    time.sleep(1)

            return {
                "total_processed": len(results),
                "successful": self.stats["successful_scholarships"],
                "failed": self.stats["failed_scholarships"],
                "no_website": self.stats["no_website_scholarships"],
                "org_logos_found": self.stats["org_logos_found"],
                "stats": self.stats,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise
