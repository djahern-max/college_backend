#!/usr/bin/env python3
"""
scripts/fix_missing_images.py

Management script for bulk image processing of institutions with tuition data
"""

import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
import argparse

# Add app directory to path
sys.path.append(".")

from app.core.database import SessionLocal
from app.services.institution import InstitutionService
from app.services.enhanced_image_extractor import EnhancedImageExtractor
from app.models.institution import ImageExtractionStatus

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'image_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ImageProcessingManager:
    """Manage bulk image processing for institutions with tuition data"""

    def __init__(self):
        self.db = SessionLocal()
        self.institution_service = InstitutionService(self.db)
        self.stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": datetime.now(),
        }

    def __del__(self):
        if hasattr(self, "db"):
            self.db.close()

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        logger.info("Generating status report...")

        diagnostics = self.institution_service.get_image_processing_diagnostics()

        print("\n" + "=" * 80)
        print("MAGICSCHOLAR IMAGE PROCESSING STATUS REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        print("TUITION DATA INSTITUTIONS:")
        tuition_data = diagnostics["tuition_data_institutions"]
        print(f"  Total institutions with tuition data: {tuition_data['total']}")
        print(f"  With images: {tuition_data['with_images']}")
        print(f"  Without images: {tuition_data['without_images']}")
        print(f"  Image coverage rate: {tuition_data['image_coverage_rate']}")
        print()

        print("PROCESSING STATUS BREAKDOWN:")
        status_data = diagnostics["processing_status"]
        for status, count in status_data.items():
            print(f"  {status.replace('_', ' ').title()}: {count}")
        print()

        print("WEBSITE AVAILABILITY:")
        website_data = diagnostics["website_availability"]
        print(f"  Institutions without websites: {website_data['no_website']}")
        print(f"  With websites: {website_data['with_website']}")
        print(f"  Website coverage rate: {website_data['website_coverage_rate']}")
        print()

        print("IMAGE QUALITY BREAKDOWN:")
        quality_data = diagnostics["image_quality"]
        for quality, count in quality_data.items():
            print(f"  {quality.replace('_', ' ').title()}: {count}")
        print()

        print("RECOMMENDED ACTIONS:")
        for i, action in enumerate(diagnostics["recommended_actions"], 1):
            print(f"  {i}. {action}")

        print("=" * 80)

        return diagnostics

    def reset_failed_processing(self) -> int:
        """Reset all failed processing statuses to pending"""
        logger.info("Resetting failed processing statuses...")
        count = self.institution_service.bulk_reset_failed_image_processing()
        logger.info(f"Reset {count} failed institutions to pending status")
        return count

    def initialize_processing_status(self) -> int:
        """Initialize processing status for institutions with no status"""
        logger.info("Initializing processing status for institutions with no status...")
        count = self.institution_service.initialize_image_processing_status()
        logger.info(f"Initialized status for {count} institutions")
        return count

    def process_batch(
        self, batch_size: int = 50, max_batches: int = None
    ) -> Dict[str, Any]:
        """Process institutions in batches"""
        logger.info(
            f"Starting batch processing (batch_size={batch_size}, max_batches={max_batches})"
        )

        extractor = EnhancedImageExtractor(self.db)
        batch_num = 0
        total_processed = 0

        while True:
            if max_batches and batch_num >= max_batches:
                logger.info(f"Reached maximum batch limit ({max_batches})")
                break

            # Get next batch of institutions to process
            institutions = (
                self.institution_service.get_institutions_ready_for_processing(
                    limit=batch_size
                )
            )

            if not institutions:
                logger.info("No more institutions ready for processing")
                break

            batch_num += 1
            logger.info(
                f"Processing batch {batch_num}: {len(institutions)} institutions"
            )

            # Process each institution in the batch
            batch_results = []
            for i, institution in enumerate(institutions, 1):
                try:
                    logger.info(
                        f"  {i}/{len(institutions)}: Processing {institution.name}"
                    )

                    result = extractor.process_institution(institution)
                    batch_results.append(result)

                    if result["status"] == "success":
                        self.stats["successful"] += 1
                        quality_score = result.get("best_image", {}).get(
                            "quality_score", 0
                        )
                        logger.info(f"    ✓ Success (quality: {quality_score})")
                    else:
                        self.stats["failed"] += 1
                        logger.warning(
                            f"    ✗ Failed: {result.get('error', 'Unknown error')}"
                        )

                    self.stats["processed"] += 1
                    total_processed += 1

                    # Add delay between requests to be respectful
                    import time

                    time.sleep(1)

                except Exception as e:
                    self.stats["failed"] += 1
                    self.stats["processed"] += 1
                    total_processed += 1
                    logger.error(f"    ✗ Exception processing {institution.name}: {e}")

            logger.info(
                f"Batch {batch_num} completed: {len([r for r in batch_results if r['status'] == 'success'])} successful, {len([r for r in batch_results if r['status'] != 'success'])} failed"
            )

            # Small break between batches
            if institutions and len(institutions) == batch_size:
                import time

                time.sleep(5)

        duration = datetime.now() - self.stats["start_time"]

        logger.info(f"Batch processing completed:")
        logger.info(f"  Total processed: {total_processed}")
        logger.info(f"  Successful: {self.stats['successful']}")
        logger.info(f"  Failed: {self.stats['failed']}")
        logger.info(f"  Duration: {duration}")

        return {
            "total_processed": total_processed,
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "duration_seconds": duration.total_seconds(),
            "batches_completed": batch_num,
        }

    def list_institutions_without_websites(self):
        """List institutions that need manual website updates"""
        institutions = self.institution_service.get_institutions_without_websites()

        print(f"\nINSTITUTIONS WITHOUT WEBSITES ({len(institutions)} total):")
        print("-" * 60)

        for inst in institutions[:20]:  # Show first 20
            print(f"  {inst.ipeds_id}: {inst.name} ({inst.city}, {inst.state})")

        if len(institutions) > 20:
            print(f"  ... and {len(institutions) - 20} more")

        print(
            f"\nThese institutions need manual website updates before image processing can proceed."
        )
        return institutions


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Manage image processing for MagicScholar institutions"
    )
    parser.add_argument(
        "command",
        choices=[
            "status",
            "reset-failed",
            "init-status",
            "process",
            "list-no-websites",
            "full-fix",
        ],
        help="Command to execute",
    )
    parser.add_argument(
        "--batch-size", type=int, default=50, help="Batch size for processing"
    )
    parser.add_argument(
        "--max-batches", type=int, help="Maximum number of batches to process"
    )
    parser.add_argument(
        "--reset-failed",
        action="store_true",
        help="Reset failed statuses before processing",
    )

    args = parser.parse_args()

    manager = ImageProcessingManager()

    try:
        if args.command == "status":
            manager.get_status_report()

        elif args.command == "reset-failed":
            count = manager.reset_failed_processing()
            print(f"Reset {count} failed institutions to pending status")

        elif args.command == "init-status":
            count = manager.initialize_processing_status()
            print(f"Initialized status for {count} institutions")

        elif args.command == "process":
            if args.reset_failed:
                manager.reset_failed_processing()
                manager.initialize_processing_status()

            result = manager.process_batch(
                batch_size=args.batch_size, max_batches=args.max_batches
            )
            print(
                f"\nProcessing completed: {result['successful']}/{result['total_processed']} successful"
            )

        elif args.command == "list-no-websites":
            manager.list_institutions_without_websites()

        elif args.command == "full-fix":
            print("Starting full image processing fix...")

            # 1. Get initial status
            print("\n1. Getting initial status...")
            diagnostics = manager.get_status_report()

            # 2. Reset failed and initialize status
            print("\n2. Resetting failed statuses...")
            reset_count = manager.reset_failed_processing()

            print("3. Initializing processing status...")
            init_count = manager.initialize_processing_status()

            # 3. Process all institutions
            print("\n4. Processing institutions...")
            result = manager.process_batch(
                batch_size=args.batch_size, max_batches=args.max_batches
            )

            # 4. Get final status
            print("\n5. Final status report...")
            manager.get_status_report()

            print(f"\nFULL FIX COMPLETED:")
            print(f"  Reset failed: {reset_count}")
            print(f"  Initialized: {init_count}")
            print(f"  Processed: {result['total_processed']}")
            print(f"  Successful: {result['successful']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Duration: {result['duration_seconds']:.1f} seconds")

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
