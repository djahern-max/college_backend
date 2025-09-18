# scripts/upload_institution_images.py
"""
Efficient script to upload images to specific institutions using ID or name matching
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


def list_all_institutions():
    """Show all institutions with their IDs and names"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        institutions = db.query(Institution).order_by(Institution.name).all()
        print(f"Found {len(institutions)} institutions:")
        print("-" * 80)
        for inst in institutions:
            print(f"ID: {inst.id:3d} | Name: {inst.name}")
            print(f"      | Location: {inst.city}, {inst.state}")
            print(f"      | Current Image: {'Yes' if inst.primary_image_url else 'No'}")
            if inst.primary_image_quality_score:
                print(f"      | Quality Score: {inst.primary_image_quality_score}")
            print("-" * 80)
    finally:
        db.close()


def search_institutions(search_term: str):
    """Search institutions by name"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        institutions = (
            db.query(Institution)
            .filter(Institution.name.ilike(f"%{search_term}%"))
            .order_by(Institution.name)
            .all()
        )

        if institutions:
            print(f"Found {len(institutions)} institutions matching '{search_term}':")
            print("-" * 80)
            for inst in institutions:
                print(f"ID: {inst.id:3d} | Name: {inst.name}")
                print(f"      | Location: {inst.city}, {inst.state}")
                print(
                    f"      | Current Image: {'Yes' if inst.primary_image_url else 'No'}"
                )
                print("-" * 80)
        else:
            print(f"No institutions found matching '{search_term}'")

    finally:
        db.close()


def upload_image_to_institution(
    institution_id: int, image_filename: str, quality_score: int = 85
):
    """Upload an image to a specific institution - keep original aspect ratio"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    uploader = DigitalOceanSpacesUploader()

    try:
        institution = (
            db.query(Institution).filter(Institution.id == institution_id).first()
        )

        if not institution:
            print(f"Institution with ID {institution_id} not found")
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
        print(f"Uploading to institution: {institution.name}")

        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # For institution photos, maintain original proportions but standardize size
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
            cdn_filename = f"institution_{institution_id}_{base_name}_optimized.jpg"

            cdn_url = uploader.upload_image(
                image_bytes=img_bytes.getvalue(),
                file_path=f"institutions/optimized/{cdn_filename}",
                content_type="image/jpeg",
            )

            if cdn_url:
                # Update database
                institution.primary_image_url = cdn_url
                institution.primary_image_quality_score = quality_score
                institution.image_extraction_status = ImageExtractionStatus.SUCCESS
                db.commit()

                print(f"SUCCESS! Updated {institution.name}")
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
    """Main menu for uploading institution images"""
    print("Institution Image Uploader")
    print("=" * 50)

    while True:
        print("\nWhat would you like to do?")
        print("1. List all institutions")
        print("2. Search institutions by name")
        print("3. Upload image to specific institution")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            list_all_institutions()

        elif choice == "2":
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_institutions(search_term)
            else:
                print("Please enter a search term")

        elif choice == "3":
            try:
                institution_id = int(input("Enter institution ID: ").strip())
                image_filename = input("Enter image filename: ").strip()
                quality_score = input(
                    "Enter quality score (1-100, default 85): "
                ).strip()

                if quality_score:
                    quality_score = int(quality_score)
                else:
                    quality_score = 85

                if upload_image_to_institution(
                    institution_id, image_filename, quality_score
                ):
                    print("\nImage uploaded successfully!")
                else:
                    print("\nUpload failed!")

            except ValueError:
                print("Please enter valid numbers for institution ID and quality score")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
