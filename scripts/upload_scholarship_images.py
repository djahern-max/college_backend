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
    """Upload an image to a specific scholarship by ID with better fitting"""
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

        image_path = f"manual_images/{image_filename}"

        if not os.path.exists(image_path):
            print(f"Image not found at {image_path}")
            return False

        print(f"Uploading {image_filename} to scholarship: {scholarship.title}")

        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Target size
            target_width, target_height = 400, 300

            # Calculate scaling to fit within target while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min(target_width / img_width, target_height / img_height)

            # Resize maintaining aspect ratio
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            # Create new image with target dimensions and dark background
            final_img = Image.new(
                "RGB", (target_width, target_height), (40, 40, 40)
            )  # Dark gray background

            # Center the resized image
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            final_img.paste(img_resized, (x_offset, y_offset))

            # Save to bytes
            img_bytes = BytesIO()
            final_img.save(img_bytes, format="JPEG", quality=90)
            img_bytes.seek(0)

            # Create unique filename for CDN
            cdn_filename = f"scholarship_{scholarship_id}_{image_filename}"

            cdn_url = uploader.upload_image(
                image_bytes=img_bytes.getvalue(),
                file_path=f"scholarships/manual/{cdn_filename}",
                content_type="image/jpeg",
            )

            if cdn_url:
                # Update database
                scholarship.primary_image_url = cdn_url
                scholarship.primary_image_quality_score = quality_score
                db.commit()

                print(f"SUCCESS! Updated {scholarship.title}")
                print(f"CDN URL: {cdn_url}")
                print(f"Image fitted with proper aspect ratio and centered")
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
                image_filename = input(
                    "Enter image filename (in manual_images/ folder): "
                ).strip()

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
