#!/usr/bin/env python3
"""
Enhanced University Image Extractor for MagicScholar College Backend
Extracts images from university websites and processes them for upload
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
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CollegeBackendImageExtractor:
    def __init__(
        self, output_dir="extracted_images", target_width=400, target_height=300
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

    def calculate_image_quality_score(self, image_info, image_type):
        """Calculate a quality score for an image (0-100) - same as service"""
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

    def load_university_data(self, csv_path):
        """Load university data from CSV file in college-backend"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} universities from {csv_path}")

            # Check what columns we have
            logger.info(f"Available columns: {list(df.columns)}")

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
                    "image_data": image_data,  # Keep for upload service
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

        # Get ID - try different column names
        institution_id = None
        for id_col in ["ipeds_id", "unitid", "UNITID", "id"]:
            if id_col in row.index:
                institution_id = row[id_col]
                break

        result = {
            "institution_id": institution_id,
            "name": school_name,
            "website": website,
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

        # Create ranking by quality
        schools_with_scores = [
            (r["name"], r["best_image"]["quality_score"])
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

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("COLLEGE BACKEND IMAGE EXTRACTION REPORT")
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
        for i, (name, score) in enumerate(schools_with_scores[:10], 1):
            logger.info(f"  {i:2d}. {name} (Score: {score})")

        if report["needs_attention"]:
            logger.info(
                f"\nSchools needing attention: {len(report['needs_attention'])}"
            )


def main():
    """Main execution function"""
    extractor = CollegeBackendImageExtractor(
        target_width=400,  # Consistent card width
        target_height=300,  # Consistent card height
    )

    # Load university data from college-backend data directory
    csv_path = "data/institutions_processed.csv"

    if not Path(csv_path).exists():
        logger.error(f"File not found: {csv_path}")
        logger.info("Available files in data directory:")
        data_dir = Path("data")
        if data_dir.exists():
            for file in data_dir.glob("*.csv"):
                logger.info(f"  {file.name}")
        return

    universities_df = extractor.load_university_data(csv_path)

    if universities_df is None:
        logger.error("Could not load university data")
        return

    print(f"\nFound {len(universities_df)} universities with websites")
    print("Sample of available data:")
    display_cols = ["name", "website"]
    if "state" in universities_df.columns:
        display_cols.append("state")
    available_cols = [col for col in display_cols if col in universities_df.columns]
    print(universities_df[available_cols].head())

    print(f"\nProcessing options:")
    print(f"1. Process all {len(universities_df)} schools")
    print(f"2. Process just 5 schools for quick test")
    print(f"3. Process just 10 schools")

    choice = input("Enter choice (1-3): ").strip()

    max_unis = None
    if choice == "2":
        max_unis = 5
    elif choice == "3":
        max_unis = 10

    print(f"\nStarting image extraction...")
    print(f"Output directory: {extractor.output_dir}")
    print(f"Target image size: {extractor.target_width}x{extractor.target_height}px")
    print(f"Processing from: {csv_path}")

    # Process universities
    extractor.process_batch(universities_df, max_universities=max_unis)

    logger.info("Image extraction complete!")
    logger.info(f"Check {extractor.output_dir} for organized images and results")
    logger.info("Next: Use admin API endpoints to upload these images to Digital Ocean")


if __name__ == "__main__":
    main()
