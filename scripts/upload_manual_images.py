#!/usr/bin/env python3
"""
Script to upload manually downloaded images to Digital Ocean Spaces
and update the database with CDN URLs.

Usage:
    python scripts/upload_manual_images.py --state ar
    python scripts/upload_manual_images.py --all
    python scripts/upload_manual_images.py --state ar --dry-run
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()


class ImageUploader:
    def __init__(self, state_code=None, dry_run=False):
        self.state_code = state_code.lower() if state_code else None
        self.dry_run = dry_run

        # Digital Ocean Spaces configuration
        if not dry_run:
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

        # Manual mappings for Arkansas schools
        # Format: filename_without_extension -> ipeds_id
        self.ar_mappings = {
            "Arkansas_State": 106458,
            "Arkansas_Tech_University": 106467,
            "Harding_University": 107044,
            "Henderson_State_University": 107071,
            "John_Brown_University": 107141,
            "South_Arkansas_University": 107983,
            "University_of_Arkansas": 106397,
            "University_Arkansas_Community_College-Morrilton": 107585,
            "University_of_Arkansas_at_Little_Rock": 106245,
            "University_of_Arkansas_at_Pine_Bluff": 106412,
            "University_Arkansas-Fort_Smith": 108092,
            "Univ_Central_Arkansas": 106704,
        }

    def sanitize_filename(self, name):
        """Convert institution name to safe filename format"""
        safe_name = re.sub(r"[^\w\s-]", "", name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name)
        return safe_name.strip("_")

    def optimize_image(self, image_path, max_width=1200):
        """Optimize image for web"""
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
            temp_path = image_path.parent / f"temp_{image_path.stem}_optimized.jpg"
            img.save(temp_path, "JPEG", quality=85, optimize=True)

            return temp_path

    def upload_to_spaces(self, local_path, s3_key):
        """Upload file to Digital Ocean Spaces"""
        if self.dry_run:
            print(f"  [DRY RUN] Would upload: {s3_key}")
            return f"{self.cdn_base_url}/{s3_key}"

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

    def get_institution_by_ipeds(self, ipeds_id):
        """Get institution details from database by IPEDS ID"""
        with self.engine.connect() as conn:
            query = text(
                """
                SELECT id, ipeds_id, name, state, city
                FROM institutions 
                WHERE ipeds_id = :ipeds_id
                LIMIT 1
            """
            )
            result = conn.execute(query, {"ipeds_id": ipeds_id})
            row = result.fetchone()

            if row:
                return {
                    "id": row[0],
                    "ipeds_id": row[1],
                    "name": row[2],
                    "state": row[3],
                    "city": row[4],
                }
        return None

    def match_by_mapping(self, filename):
        """Match filename using manual mappings"""
        # Remove file extension
        name = filename
        for ext in [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]:
            if name.endswith(ext):
                name = name[: -len(ext)]
                break

        # Check Arkansas mappings
        if name in self.ar_mappings:
            ipeds_id = self.ar_mappings[name]
            return self.get_institution_by_ipeds(ipeds_id)

        return None

    def get_image_files(self):
        """Get all image files from manual_images directory"""
        if not self.manual_images_dir.exists():
            print(f"Error: Directory {self.manual_images_dir} not found")
            return []

        image_files = []
        for ext in [
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.webp",
            "*.JPG",
            "*.JPEG",
            "*.PNG",
            "*.WEBP",
        ]:
            image_files.extend(self.manual_images_dir.glob(ext))

        return sorted(image_files)

    def process_images(self):
        """Process all images in manual_images directory"""
        image_files = self.get_image_files()

        if not image_files:
            print(f"No images found in {self.manual_images_dir}")
            return

        print(f"\n{'='*60}")
        if self.dry_run:
            print("DRY RUN MODE - No changes will be made")
        else:
            print("LIVE MODE - Changes will be saved")
        print(f"{'='*60}")
        print(f"Found {len(image_files)} images in {self.manual_images_dir}")
        if self.state_code:
            print(f"Processing images for state: {self.state_code.upper()}")
        else:
            print("Processing images for ALL states")
        print()

        uploaded_count = 0
        updated_count = 0
        skipped_count = 0
        no_match_files = []

        for image_path in image_files:
            print(f"\nProcessing: {image_path.name}")

            # Match with institution using mappings
            institution = self.match_by_mapping(image_path.name)

            if not institution:
                print(f"  ✗ No mapping found for {image_path.name}")
                no_match_files.append(image_path.name)
                skipped_count += 1
                continue

            # Check state filter
            if self.state_code and institution["state"].lower() != self.state_code:
                print(
                    f"  ⊘ Skipped (wrong state): {institution['name']} ({institution['state']})"
                )
                skipped_count += 1
                continue

            print(f"  → Matched: {institution['name']}")
            print(f"     City: {institution['city']}, {institution['state']}")
            print(f"     IPEDS: {institution['ipeds_id']}")

            # Create S3 key
            safe_name = self.sanitize_filename(institution["name"])
            state = institution["state"].lower()
            s3_key = f"institutions/{state}/{safe_name}_optimized.jpg"

            # Upload to Spaces
            cdn_url = self.upload_to_spaces(image_path, s3_key)

            if cdn_url:
                # Update database
                if not self.dry_run:
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
                else:
                    print(f"  [DRY RUN] Would update database with: {cdn_url}")

                uploaded_count += 1
                updated_count += 1

        # Print summary
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"  Images processed: {len(image_files)}")
        print(f"  Successfully matched & uploaded: {uploaded_count}")
        print(f"  Database records updated: {updated_count}")
        print(f"  Skipped: {skipped_count}")

        if no_match_files:
            print(f"\n  Files without mappings:")
            for filename in no_match_files:
                print(f"    - {filename}")
            print(f"\n  Add mappings to the script or rename files")

        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Upload manual images to Digital Ocean Spaces and update database"
    )
    parser.add_argument(
        "--state",
        type=str,
        help="State code (e.g., ar for Arkansas, ma for Massachusetts)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process images for all states",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without making changes",
    )

    args = parser.parse_args()

    if not args.all and not args.state:
        parser.error("Either --state or --all must be specified")

    state_code = None if args.all else args.state

    uploader = ImageUploader(state_code=state_code, dry_run=args.dry_run)
    uploader.process_images()


if __name__ == "__main__":
    main()
