#!/usr/bin/env python3
"""
College Image Management CLI for MagicScholar
Complete tool for managing the transition to institutions_processed.csv and enhanced image extraction
"""

import sys
import argparse
from pathlib import Path
import logging

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.services.enhanced_image_extractor import EnhancedImageExtractor
from app.models.institution import Institution, ImageExtractionStatus

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CollegeImageManager:
    """Comprehensive management tool for college images and data"""

    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def load_complete_dataset(self):
        """Load the complete institutions_processed.csv dataset"""
        logger.info("=" * 60)
        logger.info("LOADING COMPLETE INSTITUTIONS DATASET")
        logger.info("=" * 60)

        # Import and run the complete dataset loader
        from scripts.import_college_data import main as import_main

        try:
            import_main()
            logger.info("✅ Complete dataset loaded successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to load complete dataset: {e}")
            return False

        return True

    def get_dataset_stats(self):
        """Get statistics about the current dataset"""
        logger.info("=" * 60)
        logger.info("DATASET STATISTICS")
        logger.info("=" * 60)

        # Total institutions
        total = self.db.query(Institution).count()

        # By status
        with_images = (
            self.db.query(Institution)
            .filter(Institution.primary_image_url.isnot(None))
            .count()
        )

        pending = (
            self.db.query(Institution)
            .filter(
                (Institution.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Institution.image_extraction_status.is_(None))
            )
            .count()
        )

        failed = (
            self.db.query(Institution)
            .filter(Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            .count()
        )

        success = (
            self.db.query(Institution)
            .filter(
                Institution.image_extraction_status == ImageExtractionStatus.SUCCESS
            )
            .count()
        )

        # Quality stats
        high_quality = (
            self.db.query(Institution)
            .filter(Institution.primary_image_quality_score >= 80)
            .count()
        )

        good_quality = (
            self.db.query(Institution)
            .filter(Institution.primary_image_quality_score >= 60)
            .count()
        )

        # Websites
        with_websites = (
            self.db.query(Institution).filter(Institution.website.isnot(None)).count()
        )

        logger.info(f"📊 Total Institutions: {total:,}")
        logger.info(
            f"🌐 With Websites: {with_websites:,} ({with_websites/total*100:.1f}%)"
        )
        logger.info(f"🖼️  With Images: {with_images:,} ({with_images/total*100:.1f}%)")
        logger.info(f"✅ Success: {success:,}")
        logger.info(f"⏳ Pending: {pending:,}")
        logger.info(f"❌ Failed: {failed:,}")
        logger.info(f"⭐ High Quality (80+): {high_quality:,}")
        logger.info(f"👍 Good Quality (60+): {good_quality:,}")

        if with_images > 0:
            logger.info(f"📈 High Quality Rate: {high_quality/with_images*100:.1f}%")

        return {
            "total": total,
            "with_websites": with_websites,
            "with_images": with_images,
            "pending": pending,
            "failed": failed,
            "high_quality": high_quality,
        }

    def run_enhanced_extraction(
        self, limit=None, specific_ids=None, force_reprocess=False
    ):
        """Run enhanced image extraction with improved algorithms"""
        logger.info("=" * 60)
        logger.info("ENHANCED IMAGE EXTRACTION")
        logger.info("=" * 60)

        extractor = EnhancedImageExtractor(self.db)

        if specific_ids:
            logger.info(f"🎯 Processing specific institutions: {specific_ids}")
            result = extractor.process_institutions_batch(institution_ids=specific_ids)
        elif limit:
            logger.info(f"📊 Processing up to {limit} institutions")
            result = extractor.process_institutions_batch(limit=limit)
        else:
            logger.info("🔄 Processing all pending/failed institutions")
            result = extractor.process_institutions_batch()

        logger.info("=" * 60)
        logger.info("ENHANCED EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Total Processed: {result['total_processed']}")
        logger.info(f"🖼️  Successfully Uploaded: {result['successful']}")
        logger.info(f"❌ Failed: {result['failed']}")
        logger.info(f"⭐ High Quality Images: {result['high_quality']}")

        if result["stats"]["errors"]:
            logger.info(f"❌ First 5 errors:")
            for error in result["stats"]["errors"][:5]:
                logger.info(f"   - {error}")

        return result

    def test_enhanced_extraction(self, sample_size=5):
        """Test enhanced extraction on a small sample"""
        logger.info("=" * 60)
        logger.info(f"TESTING ENHANCED EXTRACTION ({sample_size} institutions)")
        logger.info("=" * 60)

        # Get a sample of institutions with websites but no images
        sample_institutions = (
            self.db.query(Institution)
            .filter(Institution.website.isnot(None))
            .filter(
                (Institution.image_extraction_status == ImageExtractionStatus.PENDING)
                | (Institution.image_extraction_status.is_(None))
                | (Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            )
            .limit(sample_size)
            .all()
        )

        if not sample_institutions:
            logger.info("No institutions available for testing")
            return

        sample_ids = [inst.ipeds_id for inst in sample_institutions]
        logger.info(
            f"Testing with institutions: {[inst.name for inst in sample_institutions]}"
        )

        result = self.run_enhanced_extraction(specific_ids=sample_ids)

        logger.info("🧪 Test completed! Review results above.")
        return result

    def delete_all_images(self, confirm=False):
        """Delete all images and reset extraction status"""
        if not confirm:
            logger.warning(
                "⚠️  This will delete ALL institution images from Digital Ocean Spaces!"
            )
            response = input("Are you sure? Type 'DELETE ALL IMAGES' to confirm: ")
            if response != "DELETE ALL IMAGES":
                logger.info("Operation cancelled")
                return False

        logger.info("=" * 60)
        logger.info("DELETING ALL INSTITUTION IMAGES")
        logger.info("=" * 60)

        # Get all institutions with images
        institutions_with_images = (
            self.db.query(Institution)
            .filter(Institution.primary_image_url.isnot(None))
            .all()
        )

        logger.info(f"Found {len(institutions_with_images)} institutions with images")

        extractor = EnhancedImageExtractor(self.db)
        deleted_count = 0

        for institution in institutions_with_images:
            try:
                # Delete from Digital Ocean Spaces
                success = extractor.spaces_manager.delete_existing_images(
                    institution.name
                )

                # Clear database fields
                institution.primary_image_url = None
                institution.primary_image_quality_score = None
                institution.logo_image_url = None
                institution.image_extraction_status = ImageExtractionStatus.PENDING
                institution.image_extraction_date = None

                if success:
                    deleted_count += 1

            except Exception as e:
                logger.error(f"Failed to delete images for {institution.name}: {e}")

        # Commit all changes
        self.db.commit()

        logger.info(f"✅ Deleted images for {deleted_count} institutions")
        logger.info("✅ Reset all extraction statuses to PENDING")

        return True

    def retry_failed_extractions(self, limit=50):
        """Retry failed extractions with enhanced algorithm"""
        logger.info("=" * 60)
        logger.info(f"RETRYING FAILED EXTRACTIONS (limit: {limit})")
        logger.info("=" * 60)

        failed_institutions = (
            self.db.query(Institution)
            .filter(Institution.image_extraction_status == ImageExtractionStatus.FAILED)
            .filter(Institution.website.isnot(None))
            .limit(limit)
            .all()
        )

        if not failed_institutions:
            logger.info("No failed institutions found to retry")
            return

        logger.info(f"Found {len(failed_institutions)} failed institutions to retry")

        failed_ids = [inst.ipeds_id for inst in failed_institutions]
        result = self.run_enhanced_extraction(specific_ids=failed_ids)

        return result

    def compare_extraction_methods(self, sample_size=10):
        """Compare old vs enhanced extraction methods"""
        logger.info("=" * 60)
        logger.info(f"COMPARING EXTRACTION METHODS ({sample_size} institutions)")
        logger.info("=" * 60)

        # Get sample institutions
        sample_institutions = (
            self.db.query(Institution)
            .filter(Institution.website.isnot(None))
            .limit(sample_size)
            .all()
        )

        logger.info(
            "This would run both old and enhanced extraction methods for comparison"
        )
        logger.info(
            "Implementation would require running both extractors and comparing results"
        )
        logger.info("Sample institutions selected:")

        for inst in sample_institutions:
            logger.info(f"  - {inst.name} ({inst.website})")

        return sample_institutions

    def show_quality_distribution(self):
        """Show distribution of image quality scores"""
        logger.info("=" * 60)
        logger.info("IMAGE QUALITY DISTRIBUTION")
        logger.info("=" * 60)

        # Quality ranges
        ranges = [
            (90, 100, "Excellent"),
            (80, 89, "Very Good"),
            (70, 79, "Good"),
            (60, 69, "Fair"),
            (50, 59, "Poor"),
            (0, 49, "Very Poor"),
        ]

        for min_score, max_score, label in ranges:
            count = (
                self.db.query(Institution)
                .filter(
                    Institution.primary_image_quality_score >= min_score,
                    Institution.primary_image_quality_score <= max_score,
                )
                .count()
            )

            if count > 0:
                logger.info(
                    f"{label:>10} ({min_score:>2}-{max_score:>2}): {count:>4} institutions"
                )

        # Show some examples of high and low quality
        logger.info("\n📸 Examples of HIGH quality images (90+):")
        high_quality_examples = (
            self.db.query(Institution)
            .filter(Institution.primary_image_quality_score >= 90)
            .limit(3)
            .all()
        )

        for inst in high_quality_examples:
            logger.info(
                f"  ⭐ {inst.name} (Score: {inst.primary_image_quality_score}) - {inst.primary_image_url}"
            )

        logger.info("\n📸 Examples of LOW quality images (below 50):")
        low_quality_examples = (
            self.db.query(Institution)
            .filter(Institution.primary_image_quality_score < 50)
            .filter(Institution.primary_image_quality_score.isnot(None))
            .limit(3)
            .all()
        )

        for inst in low_quality_examples:
            logger.info(
                f"  📉 {inst.name} (Score: {inst.primary_image_quality_score}) - {inst.primary_image_url}"
            )


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="College Image Management CLI for MagicScholar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load complete dataset
  python college_image_manager.py load-dataset
  
  # Get current statistics
  python college_image_manager.py stats
  
  # Test enhanced extraction on 5 institutions
  python college_image_manager.py test --sample-size 5
  
  # Run enhanced extraction on 100 institutions
  python college_image_manager.py extract --limit 100
  
  # Process specific institutions
  python college_image_manager.py extract --ids 100654,100663,100690
  
  # Retry failed extractions
  python college_image_manager.py retry --limit 50
  
  # Show quality distribution
  python college_image_manager.py quality
  
  # Delete all images (use with caution!)
  python college_image_manager.py delete-all
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Load dataset command
    load_parser = subparsers.add_parser(
        "load-dataset", help="Load complete institutions_processed.csv dataset"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show dataset statistics")

    # Test command
    test_parser = subparsers.add_parser(
        "test", help="Test enhanced extraction on sample"
    )
    test_parser.add_argument(
        "--sample-size", type=int, default=5, help="Number of institutions to test"
    )

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract", help="Run enhanced image extraction"
    )
    extract_parser.add_argument(
        "--limit", type=int, help="Limit number of institutions to process"
    )
    extract_parser.add_argument(
        "--ids", type=str, help="Comma-separated list of IPEDS IDs to process"
    )
    extract_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocess institutions that already have images",
    )

    # Retry command
    retry_parser = subparsers.add_parser("retry", help="Retry failed extractions")
    retry_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max number of failed institutions to retry",
    )

    # Quality command
    quality_parser = subparsers.add_parser(
        "quality", help="Show image quality distribution"
    )

    # Delete all command
    delete_parser = subparsers.add_parser(
        "delete-all", help="Delete all images (use with caution!)"
    )
    delete_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation prompt"
    )

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare extraction methods")
    compare_parser.add_argument(
        "--sample-size", type=int, default=10, help="Number of institutions to compare"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        with CollegeImageManager() as manager:
            if args.command == "load-dataset":
                manager.load_complete_dataset()

            elif args.command == "stats":
                manager.get_dataset_stats()

            elif args.command == "test":
                manager.test_enhanced_extraction(args.sample_size)

            elif args.command == "extract":
                specific_ids = None
                if args.ids:
                    specific_ids = [int(id.strip()) for id in args.ids.split(",")]

                manager.run_enhanced_extraction(
                    limit=args.limit,
                    specific_ids=specific_ids,
                    force_reprocess=args.force,
                )

            elif args.command == "retry":
                manager.retry_failed_extractions(args.limit)

            elif args.command == "quality":
                manager.show_quality_distribution()

            elif args.command == "delete-all":
                manager.delete_all_images(args.confirm)

            elif args.command == "compare":
                manager.compare_extraction_methods(args.sample_size)

    except KeyboardInterrupt:
        logger.info("\n⏹️  Operation cancelled by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
