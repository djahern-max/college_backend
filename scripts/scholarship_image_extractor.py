#!/usr/bin/env python3
# scripts/scholarship_image_extractor.py
"""
Standalone script for extracting images for scholarships
Similar to enhanced_image_extractor.py but for scholarships
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.services.scholarship_image_extractor import ScholarshipImageExtractor
from app.models.scholarship import Scholarship
from app.models.institution import ImageExtractionStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'logs/scholarship_image_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    """Get database session"""
    return next(get_db())


def display_scholarship_stats(db: Session):
    """Display current scholarship image statistics"""
    try:
        total = db.query(Scholarship).count()
        with_websites = (
            db.query(Scholarship).filter(Scholarship.website_url.isnot(None)).count()
        )
        with_images = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_url.isnot(None))
            .count()
        )

        pending = (
            db.query(Scholarship)
            .filter(
                (Scholarship.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Scholarship.image_extraction_status.is_(None))
            )
            .count()
        )

        success = (
            db.query(Scholarship)
            .filter(
                Scholarship.image_extraction_status == ImageExtractionStatus.SUCCESS
            )
            .count()
        )

        failed = (
            db.query(Scholarship)
            .filter(Scholarship.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        # Quality statistics
        high_quality = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_quality_score >= 70)
            .count()
        )

        good_quality = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_quality_score >= 50)
            .count()
        )

        logger.info("=" * 60)
        logger.info("SCHOLARSHIP IMAGE STATISTICS")
        logger.info("=" * 60)
        logger.info(f"📊 Total Scholarships: {total:,}")
        logger.info(
            f"🌐 With Websites: {with_websites:,} ({with_websites/total*100 if total > 0 else 0:.1f}%)"
        )
        logger.info(
            f"🖼️  With Images: {with_images:,} ({with_images/total*100 if total > 0 else 0:.1f}%)"
        )
        logger.info(f"✅ Success: {success:,}")
        logger.info(f"⏳ Pending: {pending:,}")
        logger.info(f"❌ Failed: {failed:,}")
        logger.info(f"⭐ High Quality (70+): {high_quality:,}")
        logger.info(f"👍 Good Quality (50+): {good_quality:,}")

        if with_images > 0:
            logger.info(f"📈 High Quality Rate: {high_quality/with_images*100:.1f}%")
            logger.info(f"📊 Good Quality Rate: {good_quality/with_images*100:.1f}%")

        return {
            "total": total,
            "with_websites": with_websites,
            "with_images": with_images,
            "pending": pending,
            "success": success,
            "failed": failed,
            "high_quality": high_quality,
            "good_quality": good_quality,
        }

    except Exception as e:
        logger.error(f"Error getting scholarship stats: {e}")
        return None


def display_sample_scholarships(db: Session, limit: int = 5):
    """Display sample scholarships"""
    try:
        scholarships = db.query(Scholarship).limit(limit).all()

        logger.info(f"\n📋 Sample of {limit} scholarships:")
        logger.info("-" * 80)
        for scholarship in scholarships:
            status = scholarship.image_extraction_status or "PENDING"
            quality = scholarship.primary_image_quality_score or "N/A"
            logger.info(
                f"ID: {scholarship.id:3d} | {scholarship.title[:40]:40} | {scholarship.organization[:20]:20} | Status: {status:8} | Quality: {quality}"
            )

    except Exception as e:
        logger.error(f"Error displaying sample scholarships: {e}")


def run_scholarship_image_extraction(
    db: Session,
    scholarship_ids: list = None,
    limit: int = None,
    force_reprocess: bool = False,
):
    """Run scholarship image extraction"""
    try:
        logger.info("=" * 60)
        logger.info("SCHOLARSHIP IMAGE EXTRACTION STARTED")
        logger.info("=" * 60)

        extractor = ScholarshipImageExtractor(db)

        if scholarship_ids:
            logger.info(f"🎯 Processing specific scholarships: {scholarship_ids}")
        elif limit:
            logger.info(f"📊 Processing up to {limit} scholarships")
        elif force_reprocess:
            logger.info("🔄 Force reprocessing all scholarships with websites")
        else:
            logger.info("🔄 Processing pending/failed scholarships")

        # Run the extraction
        result = extractor.process_scholarships_batch(
            scholarship_ids=scholarship_ids,
            limit=limit,
            force_reprocess=force_reprocess,
        )

        logger.info("=" * 60)
        logger.info("EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📊 Total Processed: {result['total_processed']}")
        logger.info(f"✅ Successful: {result['successful']}")
        logger.info(f"❌ Failed: {result['failed']}")
        logger.info(f"🌐 No Website: {result['no_website']}")
        logger.info(f"🏢 Org Logos Found: {result['org_logos_found']}")

        # Show some sample results
        if result["results"]:
            logger.info(f"\n📋 Sample Results:")
            logger.info("-" * 80)
            for i, res in enumerate(result["results"][:5]):
                status_emoji = "✅" if res["status"] == "success" else "❌"
                quality = res.get("best_image", {}).get("quality_score", "N/A")
                logger.info(
                    f"{status_emoji} {res['title'][:40]:40} | Quality: {quality} | Status: {res['status']}"
                )

        return result

    except Exception as e:
        logger.error(f"Error in scholarship image extraction: {e}")
        raise


def main():
    """Main function"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Get database session
        db = get_db_session()

        logger.info("🎓 Scholarship Image Extractor")
        logger.info("=" * 60)

        # Display current statistics
        stats = display_scholarship_stats(db)
        if not stats:
            logger.error("Could not get scholarship statistics")
            return

        # Display sample scholarships
        display_sample_scholarships(db)

        # Interactive menu
        print(f"\n🎯 PROCESSING OPTIONS:")
        print(
            f"1. Process all pending/failed scholarships ({stats['pending']} pending)"
        )
        print(f"2. Process 5 scholarships (quick test)")
        print(f"3. Process 10 scholarships")
        print(f"4. Process specific scholarship IDs")
        print(f"5. Force reprocess all scholarships with websites")
        print(f"6. Just show statistics (no processing)")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == "1":
            # Process all pending/failed
            result = run_scholarship_image_extraction(db)

        elif choice == "2":
            # Process 5 scholarships
            result = run_scholarship_image_extraction(db, limit=5)

        elif choice == "3":
            # Process 10 scholarships
            result = run_scholarship_image_extraction(db, limit=10)

        elif choice == "4":
            # Process specific IDs
            ids_input = input("Enter scholarship IDs (comma-separated): ").strip()
            try:
                scholarship_ids = [int(x.strip()) for x in ids_input.split(",")]
                result = run_scholarship_image_extraction(
                    db, scholarship_ids=scholarship_ids
                )
            except ValueError:
                logger.error("Invalid scholarship IDs format")
                return

        elif choice == "5":
            # Force reprocess all
            confirm = (
                input(
                    f"Are you sure you want to reprocess all {stats['with_websites']} scholarships? (y/N): "
                )
                .strip()
                .lower()
            )
            if confirm == "y":
                result = run_scholarship_image_extraction(db, force_reprocess=True)
            else:
                logger.info("Cancelled")
                return

        elif choice == "6":
            # Just show stats
            logger.info("Statistics displayed above")
            return

        else:
            logger.error("Invalid choice")
            return

        # Final statistics
        logger.info("\n" + "=" * 60)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 60)
        display_scholarship_stats(db)

        logger.info("\n🎉 Scholarship image extraction completed!")
        logger.info("💡 Next steps:")
        logger.info("1. Review failed extractions in admin panel")
        logger.info("2. Manually upload images for organizations without websites")
        logger.info("3. Update scholarship cards to display extracted images")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    main()
