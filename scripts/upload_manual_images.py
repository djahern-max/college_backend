# scripts/upload_manual_images.py
"""
Script to upload manually downloaded images to Digital Ocean Spaces
and update the database with CDN URLs.

This script:
1. Reads images from the manual_images directory
2. Uploads them to Digital Ocean Spaces with proper folder structure
3. Updates the institutions table with CDN URLs

Usage:
    python scripts/upload_manual_images.py --state ak
"""

import os
import sys
import re
import boto3
from pathlib import Path
from PIL import Image
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import argparse

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


class ImageUploader:
    def __init__(self, state_code):
        self.state_code = state_code.lower()

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

    def sanitize_filename(self, name):
        """Convert institution name to safe filename format"""
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r"[^\w\s-]", "", name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name)
        return safe_name.strip("_")

    def optimize_image(self, image_path, max_width=1200):
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
            temp_path = image_path.parent / f"temp_{image_path.name}"
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
            print(f"✓ Uploaded: {s3_key}")
            return cdn_url

        except Exception as e:
            print(f"✗ Error uploading {s3_key}: {str(e)}")
            return None

    def match_institution_name(self, filename):
        """Extract institution name from filename and try to match with database"""
        # Remove file extension and common prefixes
        name = filename.replace(".jpg", "").replace(".jpeg", "").replace(".png", "")
        name = re.sub(r"^(ACC-|Alaska-|alaska-)", "", name, flags=re.IGNORECASE)

        # Convert to more readable format
        name = name.replace("-", " ").replace("_", " ")
        name = re.sub(r"\s+", " ", name).strip()

        # Try to find matching institution
        with self.engine.connect() as conn:
            # Try exact match first
            query = text(
                """
                SELECT id, ipeds_id, name 
                FROM institutions 
                WHERE LOWER(state) = :state 
                AND LOWER(name) LIKE :pattern
                LIMIT 1
            """
            )

            patterns = [
                f"%{name.lower()}%",
                f"%{name.lower().split()[0]}%",
                f"%{' '.join(name.lower().split()[:2])}%",
            ]

            for pattern in patterns:
                result = conn.execute(
                    query, {"state": self.state_code, "pattern": pattern}
                )
                row = result.fetchone()
                if row:
                    return {"id": row[0], "ipeds_id": row[1], "name": row[2]}

        return None

    def process_images(self):
        """Process all images in manual_images directory for the specified state"""
        if not self.manual_images_dir.exists():
            print(f"Error: Directory {self.manual_images_dir} not found")
            return

        # Get all image files
        image_files = list(self.manual_images_dir.glob("*.[jJ][pP][gG]"))
        image_files.extend(self.manual_images_dir.glob("*.[jJ][pP][eE][gG]"))
        image_files.extend(self.manual_images_dir.glob("*.[pP][nN][gG]"))

        print(f"\nFound {len(image_files)} images in {self.manual_images_dir}")
        print(f"Processing images for state: {self.state_code.upper()}\n")

        uploaded_count = 0
        updated_count = 0

        for image_path in image_files:
            print(f"\nProcessing: {image_path.name}")

            # Match with institution
            institution = self.match_institution_name(image_path.stem)

            if not institution:
                print(f"  ✗ Could not match institution for {image_path.name}")
                print(f"    Please manually update or rename file")
                continue

            print(
                f"  → Matched: {institution['name']} (IPEDS: {institution['ipeds_id']})"
            )

            # Create S3 key with state folder structure
            safe_name = self.sanitize_filename(institution["name"])
            s3_key = f"institutions/{self.state_code}/{safe_name}_optimized.jpg"

            # Upload to Spaces
            cdn_url = self.upload_to_spaces(image_path, s3_key)

            if cdn_url:
                # Update database - simplified to match your schema
                with self.engine.connect() as conn:
                    update_query = text(
                        """
                        UPDATE institutions 
                        SET primary_image_url = :url,
                            updated_at = NOW()
                        WHERE id = :id
                    """
                    )
                    conn.execute(
                        update_query, {"url": cdn_url, "id": institution["id"]}
                    )
                    conn.commit()

                print(f"  ✓ Database updated with CDN URL")
                uploaded_count += 1
                updated_count += 1

        print(f"\n{'='*60}")
        print(f"Summary for {self.state_code.upper()}:")
        print(f"  Images uploaded: {uploaded_count}")
        print(f"  Database records updated: {updated_count}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Upload manual images to Digital Ocean Spaces and update database"
    )
    parser.add_argument(
        "--state",
        type=str,
        required=True,
        help="State code (e.g., ak for Alaska, ma for Massachusetts)",
    )

    args = parser.parse_args()

    uploader = ImageUploader(args.state)
    uploader.process_images()


if __name__ == "__main__":
    main()
