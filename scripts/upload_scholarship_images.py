# scripts/upload_scholarship_images.py
"""
Efficient script to upload images to specific scholarships using ID or title matching
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
from app.models.scholarship import Scholarship


def list_all_scholarships():
    """Show all scholarships with their IDs and titles"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        scholarships = db.query(Scholarship).all()
        print(f"Found {len(scholarships)} scholarships:")
        print("-" * 80)
        for s in scholarships:
            print(f"ID: {s.id:2d} | Title: {s.title}")
            print(f"     | Org: {s.organization}")
            print(f"     | Current Image: {'Yes' if s.primary_image_url else 'No'}")
            print("-" * 80)
    finally:
        db.close()


def upload_image_to_scholarship(
    scholarship_id: int, image_filename: str, quality_score: int = 95
):
    """Upload an image to a specific scholarship - keep original aspect ratio"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    uploader = DigitalOceanSpacesUploader()

    try:
        scholarship = (
            db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )

        if not scholarship:
            print(f"Scholarship with ID {scholarship_id} not found")
            return False

        # Look for image in current directory first, then manual_images
        image_path = image_filename
        if not os.path.exists(image_path):
            image_path = f"manual_images/{image_filename}"
            if not os.path.exists(image_path):
                image_path = f"../manual_images/{image_filename}"
                if not os.path.exists(image_path):
                    print(f"Image not found at any expected location")
                    print(
                        f"Tried: {image_filename}, manual_images/{image_filename}, ../manual_images/{image_filename}"
                    )
                    return False

        print(f"Found image at: {image_path}")
        print(f"Uploading to scholarship: {scholarship.title}")

        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # For scholarship graphics, maintain original proportions but standardize size
            # Target maximum dimensions while keeping aspect ratio
            max_width, max_height = 400, 300

            # Get original dimensions
            original_width, original_height = img.size
            print(f"Original size: {original_width}x{original_height}")

            # Calculate scaling to fit within max dimensions
            scale_w = max_width / original_width
            scale_h = max_height / original_height
            scale = min(scale_w, scale_h)

            # New dimensions maintaining aspect ratio
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            print(f"Scaled size: {new_width}x{new_height}")

            # Resize maintaining aspect ratio
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG", quality=95, optimize=True)
            img_bytes.seek(0)

            # Create unique filename for CDN
            base_name = image_filename.split(".")[0]
            cdn_filename = f"scholarship_{scholarship_id}_{base_name}_optimized.jpg"

            cdn_url = uploader.upload_image(
                image_bytes=img_bytes.getvalue(),
                file_path=f"scholarships/optimized/{cdn_filename}",
                content_type="image/jpeg",
            )

            if cdn_url:
                # Update database
                scholarship.primary_image_url = cdn_url
                scholarship.primary_image_quality_score = quality_score
                db.commit()

                print(f"SUCCESS! Updated {scholarship.title}")
                print(f"CDN URL: {cdn_url}")
                print(f"Image optimized: {new_width}x{new_height}px")
                return True
            else:
                print("Failed to upload to CDN")
                return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        db.close()


def main():
    """Main menu for uploading scholarship images"""
    print("Scholarship Image Uploader")
    print("=" * 50)

    while True:
        print("\nWhat would you like to do?")
        print("1. List all scholarships")
        print("2. Upload image to specific scholarship")
        print("3. Exit")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            list_all_scholarships()

        elif choice == "2":
            try:
                scholarship_id = int(input("Enter scholarship ID: ").strip())
                image_filename = input("Enter image filename: ").strip()

                if upload_image_to_scholarship(scholarship_id, image_filename):
                    print("\nImage uploaded successfully!")
                else:
                    print("\nUpload failed!")

            except ValueError:
                print("Please enter a valid scholarship ID number")

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
