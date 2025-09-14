# scripts/reprocess_scholarship_images.py
"""
Batch reprocess scholarships that have no images or failed extraction
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.scholarship import Scholarship, ImageExtractionStatus
from app.services.scholarship_image_extractor import ScholarshipImageExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScholarshipImageReprocessor:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_scholarships_needing_images(self):
        """Get scholarships that need image processing"""
        db = self.SessionLocal()
        try:
            scholarships = (
                db.query(Scholarship)
                .filter(
                    (Scholarship.primary_image_url.is_(None))
                    | (
                        Scholarship.image_extraction_status
                        == ImageExtractionStatus.FAILED
                    )
                    | (
                        Scholarship.image_extraction_status
                        == ImageExtractionStatus.PENDING
                    )
                )
                .filter(Scholarship.website_url.isnot(None))  # Must have a website
                .all()
            )

            return scholarships
        finally:
            db.close()

    def reprocess_batch(self, limit: int = 50):
        """Reprocess a batch of scholarships"""
        scholarships = self.get_scholarships_needing_images()[:limit]

        if not scholarships:
            logger.info("No scholarships need image processing")
            return

        logger.info(f"Reprocessing {len(scholarships)} scholarships...")

        db = self.SessionLocal()
        try:
            extractor = ScholarshipImageExtractor(db)

            for i, scholarship in enumerate(scholarships, 1):
                logger.info(
                    f"[{i}/{len(scholarships)}] Processing: {scholarship.title}"
                )

                try:
                    result = extractor.process_scholarship(scholarship)
                    if result["status"] == "success":
                        logger.info(f"✅ Success: {scholarship.title}")
                    else:
                        logger.warning(
                            f"⚠️ Failed: {scholarship.title} - {result.get('error', 'Unknown error')}"
                        )
                except Exception as e:
                    logger.error(f"❌ Error processing {scholarship.title}: {e}")

        finally:
            db.close()

    def get_statistics(self):
        """Get current image statistics"""
        db = self.SessionLocal()
        try:
            total = db.query(Scholarship).count()
            with_images = (
                db.query(Scholarship)
                .filter(Scholarship.primary_image_url.isnot(None))
                .count()
            )
            failed = (
                db.query(Scholarship)
                .filter(
                    Scholarship.image_extraction_status == ImageExtractionStatus.FAILED
                )
                .count()
            )
            pending = (
                db.query(Scholarship)
                .filter(
                    Scholarship.image_extraction_status == ImageExtractionStatus.PENDING
                )
                .count()
            )

            return {
                "total": total,
                "with_images": with_images,
                "failed": failed,
                "pending": pending,
                "no_images": total - with_images,
            }
        finally:
            db.close()


def main():
    # Update with your database URL
    DATABASE_URL = "postgresql://user:password@localhost/magicscholar"

    reprocessor = ScholarshipImageReprocessor(DATABASE_URL)

    # Show current stats
    stats = reprocessor.get_statistics()
    logger.info("Current Statistics:")
    logger.info(f"  Total scholarships: {stats['total']}")
    logger.info(f"  With images: {stats['with_images']}")
    logger.info(f"  No images: {stats['no_images']}")
    logger.info(f"  Failed: {stats['failed']}")
    logger.info(f"  Pending: {stats['pending']}")

    # Reprocess batch
    reprocessor.reprocess_batch(limit=20)

    # Show updated stats
    new_stats = reprocessor.get_statistics()
    logger.info("Updated Statistics:")
    logger.info(
        f"  With images: {new_stats['with_images']} (was {stats['with_images']})"
    )
    logger.info(f"  No images: {new_stats['no_images']} (was {stats['no_images']})")


if __name__ == "__main__":
    main()
