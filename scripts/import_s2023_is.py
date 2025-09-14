# scripts/upload_single_image.py
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


def upload_hispanic_heritage_logo():
    """Upload the Hispanic Heritage image"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    uploader = DigitalOceanSpacesUploader()

    try:
        scholarship = (
            db.query(Scholarship)
            .filter(Scholarship.title.ilike("%Hispanic Scholarship Fund%"))
            .first()
        )

        if not scholarship:
            print("Hispanic Scholarship Fund not found in database")
            return

        image_path = "manual_images/hispanic_scholarship_fund_coins.jpg"

        if not os.path.exists(image_path):
            print(f"Image not found at {image_path}")
            return

        with Image.open(image_path) as img:
            img = img.resize((400, 300), Image.LANCZOS)

            if img.mode != "RGB":
                img = img.convert("RGB")

            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG", quality=90)
            img_bytes.seek(0)

            cdn_url = uploader.upload_image(
                image_bytes=img_bytes.getvalue(),
                file_path=f"scholarships/manual/hispanic_heritage_fund_v2.jpg",
                content_type="image/jpeg",
            )

            if cdn_url:
                scholarship.primary_image_url = cdn_url
                scholarship.primary_image_quality_score = 95
                db.commit()

                print(f"Success! Updated Hispanic Scholarship Fund")
                print(f"CDN URL: {cdn_url}")
            else:
                print("Failed to upload to CDN")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    upload_hispanic_heritage_logo()
