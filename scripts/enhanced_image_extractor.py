#!/usr/bin/env python3
"""
Enhanced University Image Extractor for MagicScholar
Focuses on extracting the highest quality images with consistent sizing and ranking
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from pathlib import Path
import logging
import time
import json
import hashlib
from PIL import Image, ImageOps
import io
import math
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EnhancedImageExtractor:
    def __init__(
        self, output_dir="enhanced_images", target_width=400, target_height=300
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create organized subdirectories
        (self.output_dir / "primary").mkdir(exist_ok=True)  # Best image per school
        (self.output_dir / "logos").mkdir(exist_ok=True)  # Clean logos
        (self.output_dir / "raw").mkdir(exist_ok=True)  # Unprocessed originals

        # Image standardization settings
        self.target_width = target_width
        self.target_height = target_height

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        self.results = []
        self.failed_urls = []

    def calculate_improved_quality_score(
        self, image_info: Dict[str, Any], school_name: str
    ) -> float:
        """
        Improved quality scoring that properly prioritizes campus imagery over promotional content
        """
        score = 0.0
        width = image_info["width"]
        height = image_info["height"]
        url = image_info["url"].lower()
        image_type = image_info["image_type"]

        # Base score from dimensions (reduced weight - 0-25 points instead of 0-40)
        if width >= 1200 and height >= 800:
            score += 25
        elif width >= 800 and height >= 600:
            score += 20
        elif width >= 600 and height >= 400:
            score += 15
        elif width >= 400 and height >= 300:
            score += 10
        elif width >= 200 and height >= 150:
            score += 5

        # Aspect ratio (reduced weight - 0-5 points instead of 0-10)
        aspect_ratio = width / height if height > 0 else 0
        if 1.2 <= aspect_ratio <= 2.0:  # Good landscape ratio
            score += 5
        elif 0.8 <= aspect_ratio <= 1.2:  # Square-ish
            score += 3

        # ENHANCED: Campus-specific content analysis (0-40 points - major weight)
        campus_content_score = 0

        # High-value campus keywords (architecture, buildings, aerial views)
        premium_campus_keywords = [
            "campus",
            "aerial",
            "building",
            "tower",
            "clock",
            "library",
            "quad",
            "courtyard",
            "hall",
            "center",
            "dome",
            "arch",
            "gate",
            "plaza",
            "lawn",
            "garden",
            "brick",
            "stone",
            "architecture",
        ]

        # Medium-value institutional keywords
        institutional_keywords = [
            "university",
            "college",
            "school",
            "academic",
            "education",
            "student",
            "graduation",
            "commencement",
            "ceremony",
        ]

        # Count premium campus keywords (3 points each, max 30)
        premium_matches = sum(
            3 for keyword in premium_campus_keywords if keyword in url
        )
        campus_content_score += min(30, premium_matches)

        # Count institutional keywords (1 point each, max 10)
        institutional_matches = sum(
            1 for keyword in institutional_keywords if keyword in url
        )
        campus_content_score += min(10, institutional_matches)

        score += campus_content_score

        # Image type bonuses (adjusted to favor campus-specific types)
        if image_type == "og_image":
            score += 20  # OG images often show campus
        elif image_type == "twitter_image":
            score += 15  # Twitter images often show campus
        elif image_type == "hero":
            score += 10  # Hero images vary in quality
        elif image_type == "logo":
            score -= 10  # Penalize logos heavily (not campus imagery)
        elif image_type == "favicon":
            score -= 20  # Heavy penalty for favicons

        # ENHANCED: Detect and penalize promotional/people photos (0 to -25 points)
        people_photo_indicators = [
            "headshot",
            "portrait",
            "people",
            "person",
            "face",
            "smile",
            "professional",
            "team",
            "staff",
            "faculty",
            "student-life",
            "interview",
            "meeting",
            "conference",
            "graduation-photo",
        ]

        people_penalty = 0
        for indicator in people_photo_indicators:
            if indicator in url:
                people_penalty += 5

        # Apply penalty (max -25 points)
        score -= min(25, people_penalty)

        # ENHANCED: Reward actual campus visual elements based on typical campus image characteristics
        campus_visual_bonus = 0

        # Large images are more likely to be campus shots than headshots
        if width >= 1200 and height >= 600:
            campus_visual_bonus += 10

        # Landscape orientation favors campus shots over portrait headshots
        if aspect_ratio >= 1.5:
            campus_visual_bonus += 5

        score += campus_visual_bonus

        # File size considerations (reduced weight - 0-5 points instead of 0-10)
        size_mb = image_info["size_bytes"] / (1024 * 1024)
        if 0.5 <= size_mb <= 8.0:
            score += 5
        elif 0.1 <= size_mb <= 15.0:
            score += 2

        # ENHANCED: Penalties for non-campus content
        penalties = [
            (width < 300 or height < 200, -15),  # Too small for campus shots
            ("favicon" in url or "icon" in url, -20),  # Likely favicon
            ("logo" in url and image_type != "logo", -15),  # Logo in non-logo context
            (size_mb > 15, -10),  # Too large
            (aspect_ratio > 3.0 or aspect_ratio < 0.3, -10),  # Weird aspect ratios
            (aspect_ratio < 0.8, -10),  # Portrait orientation (likely people photos)
        ]

        for condition, penalty in penalties:
            if condition:
                score += penalty

        # ENHANCED: Bonus for established universities (based on school name recognition)
        prestigious_indicators = [
            "university",
            "state university",
            "tech",
            "institute of technology",
            "college",
            "community college",
        ]

        school_name_lower = school_name.lower()
        for indicator in prestigious_indicators:
            if indicator in school_name_lower:
                score += 5  # Small bonus for established institutions
                break

        return max(0, min(100, score))

    def load_university_data(self, csv_path):
        """Load university data from processed CSV"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} universities from {csv_path}")

            # Look for website column
            website_col = None
            for col in ["website", "website_url", "url", "web_url"]:
                if col in df.columns:
                    website_col = col
                    break

            if not website_col:
                logger.error("No website column found in data")
                return None

            # Look for name column
            name_col = None
            for col in ["name", "institution_name", "school_name", "INSTNM"]:
                if col in df.columns:
                    name_col = col
                    break

            if not name_col:
                logger.error("No name column found in data")
                return None

            # Filter to only universities with websites
            df_with_urls = df[df[website_col].notna() & (df[website_col] != "")]
            logger.info(f"Found {len(df_with_urls)} universities with websites")

            # Rename columns for consistency
            column_renames = {}
            if website_col != "website":
                column_renames[website_col] = "website"
            if name_col != "name":
                column_renames[name_col] = "name"

            if column_renames:
                df_with_urls = df_with_urls.rename(columns=column_renames)

            return df_with_urls
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None

    def clean_url(self, url):
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

    def standardize_image(self, image_data, school_name, image_type, quality_score):
        """Standardize image to consistent dimensions"""
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

            return canvas, filename

        except Exception as e:
            logger.debug(f"Failed to standardize image: {e}")
            return None, None

    def download_and_process_image(self, image_url, school_name, image_type):
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
            standardized_img, filename = self.standardize_image(
                image_data, school_name, image_type, quality_score
            )

            if standardized_img and filename:
                # Save raw image for reference
                raw_filename = f"raw_{filename}"
                raw_path = self.output_dir / "raw" / raw_filename
                with open(raw_path, "wb") as f:
                    f.write(image_data)

                # Save standardized image
                if image_type == "logo":
                    standardized_path = self.output_dir / "logos" / filename
                else:
                    standardized_path = self.output_dir / "primary" / filename

                standardized_img.save(
                    standardized_path, "JPEG", quality=85, optimize=True
                )

                return {
                    "local_path": str(standardized_path),
                    "raw_path": str(raw_path),
                    "url": image_url,
                    "original_width": original_width,
                    "original_height": original_height,
                    "standardized_width": self.target_width,
                    "standardized_height": self.target_height,
                    "size_bytes": len(image_data),
                    "quality_score": quality_score,
                    "image_type": image_type,
                }

        except Exception as e:
            logger.debug(f"Failed to download/process {image_url}: {e}")
            return None

    def extract_website_images(self, url, school_name):
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

    def select_best_image(self, school_images):
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

    def process_university(self, row):
        """Process a single university"""
        school_name = row["name"]
        website = self.clean_url(row["website"])

        if not website:
            logger.debug(f"No valid website for {school_name}")
            return None

        logger.info(f"Processing: {school_name} ({website})")

        # Get ID
        institution_id = None
        for id_col in ["ipeds_id", "unitid", "UNITID", "id"]:
            if id_col in row.index:
                institution_id = row[id_col]
                break

        # Get school metadata for ranking
        carnegie_basic = row.get("carnegie_basic", "")
        control_type = row.get("control_type", "")
        size_category = row.get("size_category", "")

        result = {
            "institution_id": institution_id,
            "name": school_name,
            "website": website,
            "carnegie_basic": carnegie_basic,
            "control_type": control_type,
            "size_category": size_category,
            "processed_at": pd.Timestamp.now().isoformat(),
            "images": {},
            "best_image": None,
            "status": "success",
        }

        try:
            # Extract all images
            extracted_images = self.extract_website_images(website, school_name)
            result["images"] = extracted_images

            # Select best image
            best_image = self.select_best_image(extracted_images)
            result["best_image"] = best_image

            # Copy best image to primary directory if not already there
            if best_image and not best_image["local_path"].endswith("primary/"):
                primary_filename = f"{school_name.replace(' ', '_')[:50]}_primary.jpg"
                primary_path = self.output_dir / "primary" / primary_filename

                # Copy standardized image
                if Path(best_image["local_path"]).exists():
                    img = Image.open(best_image["local_path"])
                    img.save(primary_path, "JPEG", quality=85)
                    best_image["primary_path"] = str(primary_path)

            image_count = len(extracted_images)
            best_score = best_image["quality_score"] if best_image else 0
            logger.info(f"  → Extracted {image_count} images, best score: {best_score}")

            if image_count == 0:
                result["status"] = "no_images_found"

        except Exception as e:
            logger.error(f"  → Failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            self.failed_urls.append(website)

        return result

    def process_batch(self, universities_df, max_universities=None):
        """Process a batch of universities"""
        # Limit number if specified
        if max_universities:
            universities_df = universities_df.head(max_universities)

        total = len(universities_df)
        logger.info(f"Processing {total} universities...")

        for idx, (_, row) in enumerate(universities_df.iterrows(), 1):
            logger.info(f"[{idx}/{total}] Processing university...")

            result = self.process_university(row)
            if result:
                self.results.append(result)

            # Be respectful - add delay between requests
            time.sleep(2)

            # Save progress every 10 universities
            if idx % 10 == 0:
                self.save_results()
                logger.info(f"Progress saved - {idx}/{total} completed")

        # Final save and analysis
        self.save_results()
        self.generate_quality_report()

    def save_results(self):
        """Save results to JSON file"""
        results_file = self.output_dir / "extraction_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

    def generate_quality_report(self):
        """Generate detailed quality and ranking report"""
        total_processed = len(self.results)
        with_images = [r for r in self.results if len(r["images"]) > 0]
        with_good_images = [
            r
            for r in self.results
            if r["best_image"] and r["best_image"]["quality_score"] >= 60
        ]

        # Quality distribution
        quality_scores = [
            r["best_image"]["quality_score"] for r in self.results if r["best_image"]
        ]
        quality_distribution = {
            "excellent_90+": len([s for s in quality_scores if s >= 90]),
            "very_good_80+": len([s for s in quality_scores if 80 <= s < 90]),
            "good_60+": len([s for s in quality_scores if 60 <= s < 80]),
            "fair_40+": len([s for s in quality_scores if 40 <= s < 60]),
            "poor_below_40": len([s for s in quality_scores if s < 40]),
        }

        # School type analysis
        school_type_quality = {}
        for result in self.results:
            if result["best_image"]:
                school_type = result.get("carnegie_basic", "Unknown")[
                    :20
                ]  # Truncate for readability
                if school_type not in school_type_quality:
                    school_type_quality[school_type] = []
                school_type_quality[school_type].append(
                    result["best_image"]["quality_score"]
                )

        # Calculate averages
        for school_type in school_type_quality:
            scores = school_type_quality[school_type]
            school_type_quality[school_type] = {
                "count": len(scores),
                "avg_quality": sum(scores) / len(scores),
                "best_score": max(scores),
            }

        # Create ranking by quality
        schools_with_scores = [
            (r["name"], r["best_image"]["quality_score"], r["carnegie_basic"])
            for r in self.results
            if r["best_image"]
        ]
        schools_with_scores.sort(key=lambda x: x[1], reverse=True)

        report = {
            "processing_summary": {
                "total_processed": total_processed,
                "with_images": len(with_images),
                "with_good_images": len(with_good_images),
                "success_rate": f"{(len(with_images)/total_processed)*100:.1f}%",
                "high_quality_rate": f"{(len(with_good_images)/total_processed)*100:.1f}%",
            },
            "quality_distribution": quality_distribution,
            "school_type_analysis": school_type_quality,
            "top_20_schools": schools_with_scores[:20],
            "needs_attention": [
                r["name"]
                for r in self.results
                if not r["best_image"] or r["best_image"]["quality_score"] < 40
            ],
        }

        # Save report
        report_file = self.output_dir / "quality_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate database integration files
        self.generate_database_integration()

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("ENHANCED EXTRACTION QUALITY REPORT")
        logger.info("=" * 60)
        logger.info(f"Total processed: {total_processed}")
        logger.info(
            f"With images: {len(with_images)} ({(len(with_images)/total_processed)*100:.1f}%)"
        )
        logger.info(
            f"High quality (60+): {len(with_good_images)} ({(len(with_good_images)/total_processed)*100:.1f}%)"
        )

        logger.info("\nQuality Distribution:")
        for quality_level, count in quality_distribution.items():
            logger.info(f"  {quality_level}: {count}")

        logger.info(f"\nTop 10 Schools by Image Quality:")
        for i, (name, score, carnegie) in enumerate(schools_with_scores[:10], 1):
            logger.info(f"  {i:2d}. {name} (Score: {score}) - {carnegie[:30]}")

        if report["needs_attention"]:
            logger.info(
                f"\nSchools needing attention: {len(report['needs_attention'])}"
            )

    def generate_database_integration(self):
        """Generate SQL migration and update scripts for database integration"""

        # 1. Create migration SQL to add image columns
        migration_sql = """-- Migration: Add image columns to institutions table
-- Run this ONCE to add the new columns

ALTER TABLE institutions 
ADD COLUMN IF NOT EXISTS primary_image_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS primary_image_quality_score INTEGER,
ADD COLUMN IF NOT EXISTS logo_image_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS image_extraction_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS image_extraction_status VARCHAR(50);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS ix_institutions_image_quality 
ON institutions(primary_image_quality_score DESC);

CREATE INDEX IF NOT EXISTS ix_institutions_image_status 
ON institutions(image_extraction_status);

-- Add comments
COMMENT ON COLUMN institutions.primary_image_url IS 'URL to the best quality standardized image for school cards';
COMMENT ON COLUMN institutions.primary_image_quality_score IS 'Quality score 0-100 for ranking/sorting schools by image quality';
COMMENT ON COLUMN institutions.logo_image_url IS 'URL to clean school logo image';
COMMENT ON COLUMN institutions.image_extraction_date IS 'When images were last extracted/updated';
COMMENT ON COLUMN institutions.image_extraction_status IS 'Status: success, failed, needs_review, etc.';
"""

        migration_file = self.output_dir / "001_add_image_columns.sql"
        with open(migration_file, "w") as f:
            f.write(migration_sql)

        # 2. Generate UPDATE statements for each processed school
        update_statements = []
        update_statements.append("-- Update statements to populate image data")
        update_statements.append("-- Run after images are hosted on your web server")
        update_statements.append(
            "-- Replace 'https://your-domain.com/images/' with your actual image hosting URL"
        )
        update_statements.append("")

        base_url = "https://your-domain.com/images/"  # User will need to replace this

        for result in self.results:
            ipeds_id = result["institution_id"]
            name = result["name"]
            status = result["status"]

            # Escape single quotes in name for SQL
            safe_name = name.replace("'", "''")

            if result["best_image"]:
                best_img = result["best_image"]
                primary_filename = Path(best_img["local_path"]).name
                primary_url = f"{base_url}primary/{primary_filename}"
                quality_score = best_img["quality_score"]

                # Logo URL if available
                logo_url = "NULL"
                if "logo" in result["images"]:
                    logo_filename = Path(result["images"]["logo"]["local_path"]).name
                    logo_url = f"'{base_url}logos/{logo_filename}'"

                update_sql = f"""UPDATE institutions SET 
    primary_image_url = '{primary_url}',
    primary_image_quality_score = {quality_score},
    logo_image_url = {logo_url},
    image_extraction_date = NOW(),
    image_extraction_status = '{status}'
WHERE ipeds_id = {ipeds_id}; -- {safe_name}"""

            else:
                # No good images found
                update_sql = f"""UPDATE institutions SET 
    primary_image_url = NULL,
    primary_image_quality_score = 0,
    logo_image_url = NULL,
    image_extraction_date = NOW(),
    image_extraction_status = '{status}'
WHERE ipeds_id = {ipeds_id}; -- {safe_name}"""

            update_statements.append(update_sql)
            update_statements.append("")

        update_file = self.output_dir / "002_update_image_data.sql"
        with open(update_file, "w") as f:
            f.write("\n".join(update_statements))

        # 3. Generate image hosting manifest for deployment
        hosting_manifest = {
            "instructions": {
                "step_1": "Upload the enhanced_images/ directory to your web server",
                "step_2": "Make sure images are accessible at: https://your-domain.com/images/",
                "step_3": "Update the base_url in 002_update_image_data.sql",
                "step_4": "Run 001_add_image_columns.sql (one time only)",
                "step_5": "Run 002_update_image_data.sql to populate the data",
            },
            "directory_structure": {
                "primary/": "Best images standardized to 400x300px for school cards",
                "logos/": "Clean school logos for headers/search results",
                "raw/": "Original unprocessed images for reference",
            },
            "image_files": [],
        }

        # List all generated images
        for result in self.results:
            if result["best_image"]:
                hosting_manifest["image_files"].append(
                    {
                        "school": result["name"],
                        "ipeds_id": result["institution_id"],
                        "primary_image": Path(result["best_image"]["local_path"]).name,
                        "quality_score": result["best_image"]["quality_score"],
                        "logos": [
                            Path(img["local_path"]).name
                            for img_type, img in result["images"].items()
                            if img_type == "logo"
                        ],
                    }
                )

        manifest_file = self.output_dir / "hosting_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(hosting_manifest, f, indent=2)

        # 4. Generate a simple Python script to verify image URLs work
        verification_script = '''#!/usr/bin/env python3
"""
Image URL Verification Script
Run this after hosting images to verify all URLs are accessible
"""

import requests
import json
from pathlib import Path

def verify_image_urls(base_url="https://your-domain.com/images/"):
    """Verify that all generated image URLs are accessible"""
    
    with open("extraction_results.json") as f:
        results = json.load(f)
    
    print(f"Verifying image URLs with base: {base_url}")
    print("="*50)
    
    success_count = 0
    total_count = 0
    
    for result in results:
        if result['best_image']:
            total_count += 1
            filename = Path(result['best_image']['local_path']).name
            url = f"{base_url}primary/{filename}"
            
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    success_count += 1
                    status = "✓"
                else:
                    status = f"✗ ({response.status_code})"
            except:
                status = "✗ (failed)"
            
            print(f"{status} {result['name'][:40]:<40} {url}")
    
    print("="*50)
    print(f"Verification complete: {success_count}/{total_count} images accessible")
    print(f"Success rate: {(success_count/total_count)*100:.1f}%")

if __name__ == "__main__":
    # Update this URL to match your hosting setup
    verify_image_urls("https://your-domain.com/images/")
'''

        verification_file = self.output_dir / "verify_hosted_images.py"
        with open(verification_file, "w") as f:
            f.write(verification_script)

        logger.info("\n" + "=" * 60)
        logger.info("DATABASE INTEGRATION FILES GENERATED")
        logger.info("=" * 60)
        logger.info(f"Migration SQL: {migration_file}")
        logger.info(f"Update SQL: {update_file}")
        logger.info(f"Hosting guide: {manifest_file}")
        logger.info(f"Verification script: {verification_file}")
        logger.info("\nNext steps:")
        logger.info("1. Host images on your web server")
        logger.info("2. Update base URL in update SQL file")
        logger.info("3. Run migration to add columns")
        logger.info("4. Run updates to populate image data")


def main():
    """Main execution function"""
    extractor = EnhancedImageExtractor(
        target_width=400,  # Consistent card width
        target_height=300,  # Consistent card height
    )

    # Load university data
    csv_path = "processed_data/image_test.csv"

    if not Path(csv_path).exists():
        logger.error(f"File not found: {csv_path}")
        return

    universities_df = extractor.load_university_data(csv_path)

    if universities_df is None:
        logger.error("Could not load university data")
        return

    print(f"\nFound {len(universities_df)} universities with websites")
    print("Sample of available data:")
    display_cols = ["name", "website"]
    if "carnegie_basic" in universities_df.columns:
        display_cols.append("carnegie_basic")
    available_cols = [col for col in display_cols if col in universities_df.columns]
    print(universities_df[available_cols].head())

    print(f"\nProcessing options:")
    print(f"1. Process all {len(universities_df)} schools in test file")
    print(f"2. Process just 5 schools for quick test")
    print(f"3. Process just 10 schools")

    choice = input("Enter choice (1-3): ").strip()

    max_unis = None
    if choice == "2":
        max_unis = 5
    elif choice == "3":
        max_unis = 10

    print(f"\nStarting enhanced image extraction...")
    print(f"Output directory: {extractor.output_dir}")
    print(f"Target image size: {extractor.target_width}x{extractor.target_height}px")

    # Process universities
    extractor.process_batch(universities_df, max_universities=max_unis)

    logger.info("Enhanced processing complete!")
    logger.info(f"Check {extractor.output_dir} for organized images and quality report")


if __name__ == "__main__":
    main()
