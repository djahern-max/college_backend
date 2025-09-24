# scripts/upload_ma_institution_images.py
"""
Massachusetts-focused script to upload images to institutions
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


def list_ma_institutions():
    """Show all Massachusetts institutions with their IDs and names"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        institutions = (
            db.query(Institution)
            .filter(Institution.state == "MA")
            .order_by(Institution.name)
            .all()
        )

        print(f"Found {len(institutions)} Massachusetts institutions:")
        print("=" * 80)
        for inst in institutions:
            status = "✅ Has Image" if inst.primary_image_url else "❌ No Image"
            quality = (
                f" (Quality: {inst.primary_image_quality_score})"
                if inst.primary_image_quality_score
                else ""
            )

            print(f"ID: {inst.id:3d} | {inst.name}")
            print(f"      | {inst.city}, MA")
            print(f"      | {status}{quality}")

            if inst.website:
                print(f"      | Website: {inst.website}")
            print("-" * 80)

        # Summary statistics
        with_images = sum(1 for inst in institutions if inst.primary_image_url)
        print(f"\nSUMMARY: {with_images}/{len(institutions)} institutions have images")

    finally:
        db.close()


def show_ma_institutions_needing_images():
    """Show MA institutions that need images"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        institutions = (
            db.query(Institution)
            .filter(Institution.state == "MA")
            .filter(Institution.primary_image_url.is_(None))
            .order_by(Institution.name)
            .all()
        )

        if institutions:
            print(f"Found {len(institutions)} MA institutions needing images:")
            print("=" * 80)
            for inst in institutions:
                print(f"ID: {inst.id:3d} | {inst.name}")
                print(f"      | {inst.city}, MA")
                if inst.website:
                    print(f"      | Website: {inst.website}")
                print("-" * 80)
        else:
            print("All MA institutions have images! 🎉")

    finally:
        db.close()


def show_ma_institutions_with_poor_images():
    """Show MA institutions with low quality images that need replacement"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        institutions = (
            db.query(Institution)
            .filter(Institution.state == "MA")
            .filter(Institution.primary_image_quality_score < 60)
            .filter(Institution.primary_image_url.isnot(None))
            .order_by(Institution.primary_image_quality_score)
            .all()
        )

        if institutions:
            print(
                f"Found {len(institutions)} MA institutions with poor quality images:"
            )
            print("=" * 80)
            for inst in institutions:
                print(f"ID: {inst.id:3d} | {inst.name}")
                print(f"      | {inst.city}, MA")
                print(f"      | Quality Score: {inst.primary_image_quality_score}")
                if inst.website:
                    print(f"      | Website: {inst.website}")
                print("-" * 80)
        else:
            print("All MA institutions have good quality images! 🎉")

    finally:
        db.close()


def upload_image_to_ma_institution(
    institution_id: int, image_filename: str, quality_score: int = 85
):
    """Upload an image to a specific MA institution"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    uploader = DigitalOceanSpacesUploader()

    try:
        institution = (
            db.query(Institution)
            .filter(Institution.id == institution_id)
            .filter(Institution.state == "MA")  # Ensure it's a MA institution
            .first()
        )

        if not institution:
            print(f"Massachusetts institution with ID {institution_id} not found")
            return False

        # Look for image in multiple locations
        possible_paths = [
            image_filename,
            f"manual_images/{image_filename}",
            f"../manual_images/{image_filename}",
            f"ma_images/{image_filename}",  # New MA-specific folder
            f"../ma_images/{image_filename}",
        ]

        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break

        if not image_path:
            print(f"Image not found at any expected location:")
            for path in possible_paths:
                print(f"  Tried: {path}")
            return False

        print(f"Found image at: {image_path}")
        print(f"Uploading to MA institution: {institution.name}")

        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Maintain original proportions but standardize size
            max_width, max_height = 400, 300
            original_width, original_height = img.size

            print(f"Original size: {original_width}x{original_height}")

            # Calculate scaling to fit within max dimensions
            scale_w = max_width / original_width
            scale_h = max_height / original_height
            scale = min(scale_w, scale_h)

            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            print(f"Optimized size: {new_width}x{new_height}")

            # Resize maintaining aspect ratio
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG", quality=95, optimize=True)
            img_bytes.seek(0)

            # Create unique filename for CDN
            base_name = os.path.splitext(image_filename)[0]
            cdn_filename = f"ma_institution_{institution_id}_{base_name}_optimized.jpg"

            cdn_url = uploader.upload_image(
                image_bytes=img_bytes.getvalue(),
                file_path=f"institutions/ma/{cdn_filename}",  # MA-specific folder
                content_type="image/jpeg",
            )

            if cdn_url:
                # Update database
                institution.primary_image_url = cdn_url
                institution.primary_image_quality_score = quality_score
                institution.image_extraction_status = ImageExtractionStatus.SUCCESS
                db.commit()

                print(f"✅ SUCCESS! Updated {institution.name}")
                print(f"CDN URL: {cdn_url}")
                print(f"Image optimized: {new_width}x{new_height}px")
                return True
            else:
                print("❌ Failed to upload to CDN")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()


def batch_upload_ma_images():
    """Batch upload images for MA institutions based on naming convention"""
    print("Batch upload for MA institutions")
    print("Expected naming: institution_[ID]_[description].jpg")
    print("Example: institution_123_campus.jpg")

    # Look for images in various directories
    image_dirs = [".", "manual_images", "../manual_images", "ma_images", "../ma_images"]

    found_images = []
    for directory in image_dirs:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.lower().startswith(
                    "institution_"
                ) and filename.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".webp", ".avif")
                ):
                    # Extract institution ID from filename
                    try:
                        parts = filename.split("_")
                        if len(parts) >= 2:
                            institution_id = int(parts[1])
                            found_images.append(
                                (institution_id, os.path.join(directory, filename))
                            )
                    except ValueError:
                        continue

    if not found_images:
        print("No images found with naming convention institution_[ID]_*.jpg")
        return

    print(f"Found {len(found_images)} images to upload:")
    for inst_id, path in found_images:
        print(f"  Institution {inst_id}: {os.path.basename(path)}")

    confirm = input("\nProceed with batch upload? (y/N): ").strip().lower()
    if confirm != "y":
        print("Batch upload cancelled")
        return

    successful = 0
    failed = 0

    for inst_id, image_path in found_images:
        filename = os.path.basename(image_path)
        print(f"\nUploading {filename} to institution {inst_id}...")

        if upload_image_to_ma_institution(inst_id, image_path, 85):
            successful += 1
        else:
            failed += 1

    print(f"\n📊 Batch upload complete:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")


def main():
    """Main menu for MA institution image management"""
    print("🏫 Massachusetts Institution Image Manager")
    print("=" * 50)

    while True:
        print("\nWhat would you like to do?")
        print("1. List all MA institutions")
        print("2. Show MA institutions needing images")
        print("3. Show MA institutions with poor quality images")
        print("4. Upload image to specific MA institution")
        print("5. Batch upload MA images")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == "1":
            list_ma_institutions()

        elif choice == "2":
            show_ma_institutions_needing_images()

        elif choice == "3":
            show_ma_institutions_with_poor_images()

        elif choice == "4":
            try:
                institution_id = int(input("Enter MA institution ID: ").strip())
                image_filename = input("Enter image filename: ").strip()
                quality_score = input(
                    "Enter quality score (1-100, default 85): "
                ).strip()

                if quality_score:
                    quality_score = int(quality_score)
                else:
                    quality_score = 85

                if upload_image_to_ma_institution(
                    institution_id, image_filename, quality_score
                ):
                    print("\n✅ Image uploaded successfully!")
                else:
                    print("\n❌ Upload failed!")

            except ValueError:
                print("Please enter valid numbers for institution ID and quality score")

        elif choice == "5":
            batch_upload_ma_images()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()
