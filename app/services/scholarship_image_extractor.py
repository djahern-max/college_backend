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

    def select_best_image(
        self, scholarship_images: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best image with more relaxed quality requirements for scholarships
        """
        if not scholarship_images:
            return None

        sorted_images = sorted(
            scholarship_images.values(), key=lambda x: x["quality_score"], reverse=True
        )

        # RELAXED THRESHOLDS - More forgiving for scholarship images
        priorities = [
            ("org_logo", 25),  # Organization logos are great for scholarships
            ("og_image", 20),  # Lowered from 30 to 20
            ("twitter_image", 18),  # Lowered from 25 to 18
            ("hero", 15),  # Lowered from much higher to 15
            ("logo", 25),  # Organization branding
            ("favicon", 10),  # Very low but still possible
        ]

        # Try each priority tier
        for img_type, min_score in priorities:
            for img in sorted_images:
                if img["image_type"] == img_type and img["quality_score"] >= min_score:
                    return img

        # Ultimate fallback - accept ANY image with score > 5
        for img in sorted_images:
            if img["quality_score"] >= 5:
                return img

        # Last resort - return best available regardless of score
        return sorted_images[0] if sorted_images else None

    def _analyze_scholarship_content(
        self, url: str, image_type: str, organization: str, alt_text: str = ""
    ) -> int:
        """
        Enhanced content analysis that heavily penalizes generic imagery
        """
        content_score = 0
        url_lower = url.lower()
        org_lower = organization.lower()
        alt_lower = alt_text.lower()

        # HEAVY penalties for generic/inappropriate imagery (-20 to -30 points)
        generic_penalties = [
            (["headshot", "portrait", "professional", "business", "exec"], -25),
            (["stock", "shutterstock", "getty", "istock"], -30),
            (["meeting", "conference", "office", "desk"], -20),
            (["person", "people", "man", "woman", "ceo", "director"], -15),
            (["generic", "placeholder", "default", "temp"], -25),
            (["staff", "employee", "team", "board"], -20),
        ]

        for keywords, penalty in generic_penalties:
            if any(
                keyword in url_lower or keyword in alt_lower for keyword in keywords
            ):
                content_score += penalty
                break  # Don't stack penalties

        # Strong bonuses for scholarship-relevant imagery (+10 to +25 points)
        scholarship_bonuses = [
            (["scholarship", "award", "grant", "fellowship"], +25),
            (["graduate", "graduation", "ceremony", "diploma"], +20),
            (["student", "students", "scholar", "scholars"], +18),
            (["winner", "recipient", "awardee", "honoree"], +20),
            (["logo", "seal", "emblem", "badge"], +15),
            (["program", "foundation", "fund", "education"], +12),
            (["academic", "achievement", "excellence", "merit"], +15),
        ]

        for keywords, bonus in scholarship_bonuses:
            if any(
                keyword in url_lower or keyword in alt_lower for keyword in keywords
            ):
                content_score += bonus
                break

        # Organization name matching (+15 points)
        org_words = [word for word in org_lower.split() if len(word) > 3]
        for word in org_words:
            if word in url_lower or word in alt_lower:
                content_score += 15
                break

        return max(-30, min(25, content_score))

    def _calculate_scholarship_quality_score(
        self,
        width: int,
        height: int,
        size_bytes: int,
        image_type: str,
        url: str,
        organization: str,
        alt_text: str = "",  # NEW parameter
    ) -> int:
        """
        UPDATED: Calculate quality score with alt text analysis
        """
        score = 0

        # Dimension scoring (more lenient)
        if width > 0 and height > 0:
            ratio = width / height
            if 0.5 <= ratio <= 4.0:  # Much more lenient aspect ratio
                score += 25
            else:
                score += 10  # Still give some points for any dimensions

        # Size scoring (more lenient)
        if size_bytes > 50000:  # 50KB+
            score += 15
        elif size_bytes > 20000:  # 20KB+
            score += 12
        elif size_bytes > 10000:  # 10KB+
            score += 8
        elif size_bytes > 5000:  # 5KB+
            score += 4

        # Image type scoring (more generous)
        type_scores = {
            "og_image": 35,  # Increased
            "twitter_image": 30,  # Increased
            "scholarship_image": 40,  # NEW: Highest for scholarship-specific content
            "program_image": 35,  # NEW: High for program imagery
            "hero": 30,  # Increased
            "org_logo": 25,
            "cms_image": 25,  # NEW: CMS images
            "large_image": 20,  # NEW: Any large image
            "favicon": 5,
        }
        score += type_scores.get(image_type, 15)  # Higher default

        # Enhanced content analysis with alt text
        content_score = self._analyze_scholarship_content(
            url, image_type, organization, alt_text
        )
        score += content_score

        # More lenient penalties
        penalties = [
            (width < 150 or height < 100, -10),  # Less strict size penalty
            ("favicon" in url.lower(), -15),  # Less harsh favicon penalty
            (size_bytes > 10 * 1024 * 1024, -5),  # Less harsh large file penalty
        ]

        for condition, penalty in penalties:
            if condition:
                score += penalty

        return max(5, min(100, score))  # Minimum score of 5 instead of 0

    def extract_images_from_scholarship_website(
        self, url: str, organization: str
    ) -> Dict[str, Dict]:
        """
        FIXED: Extract images from scholarship organization website
        Now properly finds images that exist on these sites
        """
        extracted_images = {}

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # 1. Extract Open Graph image (same as before, but lower threshold)
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                og_url = urljoin(url, og_image.get("content"))
                processed = self.download_and_process_scholarship_image(
                    og_url, organization, "og_image"
                )
                if (
                    processed and processed["quality_score"] > 10
                ):  # Much lower threshold
                    extracted_images["og_image"] = processed

            # 2. Extract Twitter image (same as before, but lower threshold)
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image and twitter_image.get("content"):
                twitter_url = urljoin(url, twitter_image.get("content"))
                processed = self.download_and_process_scholarship_image(
                    twitter_url, organization, "twitter_image"
                )
                if (
                    processed and processed["quality_score"] > 10
                ):  # Much lower threshold
                    extracted_images["twitter_image"] = processed

            # 3. NEW: Extract large images (this was completely missing!)
            all_images = soup.find_all("img")
            large_images_found = 0

            for img in all_images:
                src = img.get("src")
                if not src:
                    continue

                # Skip tiny/navigation images
                skip_keywords = [
                    "icon",
                    "favicon",
                    "nav",
                    "menu",
                    "arrow",
                    "button",
                    "social",
                ]
                if any(keyword in src.lower() for keyword in skip_keywords):
                    continue

                # Skip very small explicit dimensions
                width = img.get("width")
                height = img.get("height")
                if width and height:
                    try:
                        w, h = int(width), int(height)
                        if w < 200 or h < 150:  # Skip small images
                            continue
                    except:
                        pass

                # Get alt text for better categorization
                alt_text = img.get("alt", "").lower()

                # Determine image type based on content
                image_type = "large_image"  # default
                if any(
                    keyword in src.lower() or keyword in alt_text
                    for keyword in [
                        "scholarship",
                        "award",
                        "scholar",
                        "graduate",
                        "student",
                    ]
                ):
                    image_type = "scholarship_image"
                elif any(
                    keyword in src.lower() or keyword in alt_text
                    for keyword in ["hero", "banner", "main"]
                ):
                    image_type = "hero"
                elif any(
                    keyword in src.lower() or keyword in alt_text
                    for keyword in ["about", "program", "mission", "vision"]
                ):
                    image_type = "program_image"

                img_url = urljoin(url, src)
                processed = self.download_and_process_scholarship_image(
                    img_url, organization, image_type, alt_text
                )

                if processed and processed["quality_score"] > 15:  # Very low threshold
                    # Keep the best image of each type
                    key = f"{image_type}_{large_images_found}"
                    extracted_images[key] = processed
                    large_images_found += 1

                    # Limit to prevent too many requests
                    if large_images_found >= 10:
                        break

            # 4. Enhanced organization logo selectors (keep existing logic)
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
                for logo_img in logo_imgs[:2]:
                    if logo_img.get("src"):
                        logo_url = urljoin(url, logo_img.get("src"))
                        alt_text = logo_img.get("alt", "")
                        processed = self.download_and_process_scholarship_image(
                            logo_url, organization, "org_logo", alt_text
                        )

                        if (
                            processed and processed["quality_score"] > 10
                        ):  # Lower threshold
                            if (
                                "org_logo" not in extracted_images
                                or processed["quality_score"]
                                > extracted_images["org_logo"]["quality_score"]
                            ):
                                extracted_images["org_logo"] = processed

            # 5. NEW: Look for WordPress uploads and common CMS patterns
            # Many scholarship sites use WordPress/CMS with predictable image patterns
            wp_selectors = [
                'img[src*="wp-content" i]',
                'img[src*="uploads" i]',
                'img[src*="media" i]',
                'img[src*="assets" i]',
                'img[src*="images" i]',
            ]

            wp_images_found = 0
            for selector in wp_selectors:
                wp_imgs = soup.select(selector)
                for wp_img in wp_imgs[:5]:  # Limit per selector
                    src = wp_img.get("src")
                    if src and wp_images_found < 5:  # Overall limit
                        # Skip tiny images
                        if any(
                            skip in src.lower() for skip in ["thumb", "icon", "small"]
                        ):
                            continue

                        img_url = urljoin(url, src)
                        alt_text = wp_img.get("alt", "")
                        processed = self.download_and_process_scholarship_image(
                            img_url, organization, "cms_image", alt_text
                        )

                        if processed and processed["quality_score"] > 15:
                            key = f"cms_image_{wp_images_found}"
                            extracted_images[key] = processed
                            wp_images_found += 1

            return extracted_images

        except Exception as e:
            logger.error(f"Error extracting images from {url}: {e}")
            return {}

    def download_and_process_scholarship_image(
        self, image_url: str, organization: str, image_type: str, alt_text: str = ""
    ) -> Optional[Dict]:
        """
        UPDATED: Download and process a scholarship image with alt text analysis
        """
        try:
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()

            # Get image info
            image_info = self.get_image_info(response.content)
            if not image_info:
                return None

            # Calculate quality score using scholarship-specific logic WITH alt text
            quality_score = self._calculate_scholarship_quality_score(
                image_info["width"],
                image_info["height"],
                image_info["size_bytes"],
                image_type,
                image_url,
                organization,
                alt_text,  # Pass alt text for better scoring
            )

            # MUCH MORE LENIENT: Skip only very low quality images
            if quality_score < 5:  # Was 15, now 5
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
                "processed_bytes": processed_image,  # Add this for consistency
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
                # UPDATED: Use the new select_best_image method instead of max()
                best_image = self.select_best_image(extracted_images)

                if not best_image:
                    result["status"] = "no_suitable_images"
                    scholarship.image_extraction_status = ImageExtractionStatus.FAILED
                    self.stats["failed_scholarships"] += 1
                else:
                    result["best_image"] = best_image

                    # Upload to CDN
                    primary_url = self.uploader.upload_image(
                        best_image[
                            "processed_bytes"
                        ],  # Note: processed_bytes, not image_data
                        f"scholarship-images/primary/{scholarship.id}.jpg",
                        "image/jpeg",
                    )

                    if primary_url:
                        result["cdn_urls"]["primary"] = primary_url
                        scholarship.primary_image_url = primary_url
                        scholarship.primary_image_quality_score = best_image[
                            "quality_score"
                        ]
                        scholarship.image_extraction_status = (
                            ImageExtractionStatus.SUCCESS
                        )

                        # Upload logo separately if we found one
                        if (
                            "org_logo" in extracted_images
                            and extracted_images["org_logo"] != best_image
                        ):
                            logo_url = self.uploader.upload_image(
                                extracted_images["org_logo"]["processed_bytes"],
                                f"scholarship-images/logos/{scholarship.id}.jpg",
                                "image/jpeg",
                            )
                            if logo_url:
                                result["cdn_urls"]["logo"] = logo_url
                                scholarship.logo_image_url = logo_url
                                self.stats["org_logos_found"] += 1

                        self.stats["successful_scholarships"] += 1
                    else:
                        result["status"] = "upload_failed"
                        scholarship.image_extraction_status = (
                            ImageExtractionStatus.FAILED
                        )
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
