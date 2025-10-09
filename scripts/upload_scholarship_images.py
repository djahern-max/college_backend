# scripts/upload_scholarship_images.py
"""
Script to upload scholarship images to Digital Ocean Spaces
and update the database with CDN URLs.

This script:
1. Reads images from the manual_images directory
2. Uploads them to Digital Ocean Spaces under scholarships/ folder
3. Updates the scholarships table with CDN URLs

Usage:
    python scripts/upload_scholarship_images.py
"""

import os
import sys
import re
import boto3
from pathlib import Path
from PIL import Image
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


class ScholarshipImageUploader:
    def __init__(self):
        # Digital Ocean Spaces configuration
        self.s3_client = boto3.client(
            "s3",
            region_name=os.getenv("DIGITAL_OCEAN_SPACES_REGION"),
            endpoint_url=os.getenv("DIGITAL_OCEAN_SPACES_ENDPOINT"),
            aws_access_key_id=os.getenv("DIGITAL_OCEAN_SPACES_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("DIGITAL_OCEAN_SPACES_SECRET_KEY"),
        )

        self.bucket_name = os.getenv("DIGITAL_OCEAN_SPACES_BUCKET")
        self.cdn_base_url = os.getenv("IMAGE_CDN_BASE_URL")

        # Database configuration
        db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(db_url)

        # Paths
        self.project_root = Path(__file__).parent.parent
        self.manual_images_dir = self.project_root / "manual_images"

        # Mapping of image filenames to scholarship titles
        self.image_mappings = {
            "cocacola.jpg": "Coca-Cola Scholars Program",
            "GoogleScholarship.jpg": "Google Lime Scholarship",
            "pellGrant.jpg": "Pell Grant",
            "elksScholarship.webp": "Elks National Foundation Most Valuable Student",
            "NationalMeritScholarship.webp": "National Merit Scholarship",
            "uncf.jpg": "UNCF General Scholarship",
        }

    def sanitize_filename(self, name):
        """Convert scholarship name to safe filename format"""
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r"[^\w\s-]", "", name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name)
        return safe_name.lower().strip("_")

    def optimize_image(self, image_path, max_width=800):
        """Optimize image for web with proper quality"""
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Save optimized to temporary file
            temp_path = image_path.parent / f"temp_{image_path.stem}.jpg"
            img.save(temp_path, "JPEG", quality=85, optimize=True)

            return temp_path

    def upload_to_spaces(self, local_path, s3_key):
        """Upload file to Digital Ocean Spaces"""
        try:
            # Optimize image first
            optimized_path = self.optimize_image(local_path)

            with open(optimized_path, "rb") as file:
                self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        "ACL": "public-read",
                        "ContentType": "image/jpeg",
                        "CacheControl": "max-age=31536000",
                    },
                )

            # Clean up temp file
            optimized_path.unlink()

            cdn_url = f"{self.cdn_base_url}/{s3_key}"
            print(f"  ✓ Uploaded: {s3_key}")
            return cdn_url

        except Exception as e:
            print(f"  ✗ Error uploading {s3_key}: {str(e)}")
            return None

    def get_scholarship_by_title(self, title):
        """Get scholarship ID from database by title"""
        with self.engine.connect() as conn:
            query = text(
                """
                SELECT id, title
                FROM scholarships
                WHERE title = :title
                LIMIT 1
            """
            )
            result = conn.execute(query, {"title": title})
            row = result.fetchone()
            if row:
                return {"id": row[0], "title": row[1]}
        return None

    def process_images(self):
        """Process all scholarship images in manual_images directory"""
        if not self.manual_images_dir.exists():
            print(f"Error: Directory {self.manual_images_dir} not found")
            return

        print(f"\nProcessing scholarship images from {self.manual_images_dir}\n")

        uploaded_count = 0
        updated_count = 0
        skipped_count = 0

        for filename, scholarship_title in self.image_mappings.items():
            image_path = self.manual_images_dir / filename

            if not image_path.exists():
                print(f"✗ Image not found: {filename}")
                skipped_count += 1
                continue

            print(f"\nProcessing: {filename}")
            print(f"  → Scholarship: {scholarship_title}")

            # Get scholarship from database
            scholarship = self.get_scholarship_by_title(scholarship_title)

            if not scholarship:
                print(f"  ✗ Scholarship not found in database: {scholarship_title}")
                skipped_count += 1
                continue

            # Create S3 key with scholarships folder structure
            safe_name = self.sanitize_filename(scholarship["title"])
            s3_key = f"scholarships/{safe_name}.jpg"

            # Upload to Spaces
            cdn_url = self.upload_to_spaces(image_path, s3_key)

            if cdn_url:
                # Update database
                with self.engine.connect() as conn:
                    update_query = text(
                        """
                        UPDATE scholarships
                        SET primary_image_url = :url,
                            updated_at = NOW()
                        WHERE id = :id
                    """
                    )
                    conn.execute(
                        update_query, {"url": cdn_url, "id": scholarship["id"]}
                    )
                    conn.commit()

                print(f"  ✓ Database updated with CDN URL")
                print(f"  ✓ URL: {cdn_url}")
                uploaded_count += 1
                updated_count += 1

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Images uploaded: {uploaded_count}")
        print(f"  Database records updated: {updated_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"{'='*60}\n")

    def list_scholarships(self):
        """List all scholarships in the database"""
        with self.engine.connect() as conn:
            query = text(
                """
                SELECT id, title, organization, primary_image_url
                FROM scholarships
                ORDER BY title
            """
            )
            result = conn.execute(query)
            rows = result.fetchall()

            print("\nCurrent Scholarships in Database:")
            print("=" * 80)
            for row in rows:
                image_status = "✓ Has image" if row[3] else "✗ No image"
                print(f"ID: {row[0]}")
                print(f"  Title: {row[1]}")
                print(f"  Organization: {row[2]}")
                print(f"  Image: {image_status}")
                if row[3]:
                    print(f"  URL: {row[3]}")
                print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload scholarship images to Digital Ocean Spaces"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all scholarships in the database",
    )

    args = parser.parse_args()

    uploader = ScholarshipImageUploader()

    if args.list:
        uploader.list_scholarships()
    else:
        uploader.process_images()


if __name__ == "__main__":
    main()
