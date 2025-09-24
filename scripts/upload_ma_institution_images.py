# scripts/upload_ma_institution_images.py
"""
Simple script to upload images for the 12 curated Massachusetts schools
"""
import sys
import os
from PIL import Image
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.image_extractor import DigitalOceanSpacesUploader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.institution import Institution, ImageExtractionStatus


# Your curated MA schools from InstitutionService
CURATED_MA_SCHOOLS = {
    166027: "Harvard.webp",  # Harvard University
    166683: "MIT.png",  # Massachusetts Institute of Technology
    164988: "Boston_University.webp",  # Boston University
    168342: "Williams.jpg",  # Williams College
    164465: "amherst_college.jpg",  # Amherst College
    168218: "Wellesley_College.jpg",  # Wellesley College
    168148: "Tufts_University.jpeg",  # Tufts University
    164924: "Boston_College.jpeg",  # Boston College
    167358: "Northeastern.webp",  # Northeastern University
    166629: "UMASS_amherst.jpg",  # University of Massachusetts-Amherst
    165015: "BrandeisUniversity.jpg",  # Brandeis University
    167835: "SmithCollege.webp",  # Smith College
}


def upload_curated_ma_images():
    """Upload images for all 12 curated Massachusetts schools"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    uploader = DigitalOceanSpacesUploader()

    successful = 0
    failed = 0

    print("Uploading images for 12 curated Massachusetts schools...")
    print("=" * 60)

    for ipeds_id, filename in CURATED_MA_SCHOOLS.items():
        try:
            # Get institution from database
            institution = (
                db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
            )

            if not institution:
                print(f"Institution with IPEDS ID {ipeds_id} not found")
                failed += 1
                continue

            # Find image file
            image_path = None
            for directory in ["manual_images", "../manual_images", "."]:
                full_path = os.path.join(directory, filename)
                if os.path.exists(full_path):
                    image_path = full_path
                    break

            if not image_path:
                print(f"Image {filename} not found for {institution.name}")
                failed += 1
                continue

            print(f"Uploading {filename} for {institution.name}...")

            # Process and upload image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize to standard dimensions while maintaining aspect ratio
                max_width, max_height = 400, 300
                original_width, original_height = img.size

                scale_w = max_width / original_width
                scale_h = max_height / original_height
                scale = min(scale_w, scale_h)

                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                img = img.resize((new_width, new_height), Image.LANCZOS)

                # Save to bytes
                img_bytes = BytesIO()
                img.save(img_bytes, format="JPEG", quality=95, optimize=True)
                img_bytes.seek(0)

                # Create CDN filename
                base_name = os.path.splitext(filename)[0]
                cdn_filename = f"ma_curated_{ipeds_id}_{base_name}_optimized.jpg"

                # Upload to CDN
                cdn_url = uploader.upload_image(
                    image_bytes=img_bytes.getvalue(),
                    file_path=f"institutions/ma/{cdn_filename}",
                    content_type="image/jpeg",
                )

                if cdn_url:
                    # Update database
                    institution.primary_image_url = cdn_url
                    institution.primary_image_quality_score = 85
                    institution.image_extraction_status = ImageExtractionStatus.SUCCESS
                    db.commit()

                    print(f"SUCCESS: {institution.name} - Updated successfully")
                    successful += 1
                else:
                    print(f"FAILED: {institution.name} - CDN upload failed")
                    failed += 1

        except Exception as e:
            print(f"ERROR processing {filename}: {str(e)}")
            failed += 1

    db.close()

    print("=" * 60)
    print(f"Upload Complete:")
    print(f"Successful: {successful}/12")
    print(f"Failed: {failed}/12")

    return successful, failed


if __name__ == "__main__":
    upload_curated_ma_images()
