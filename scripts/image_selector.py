#!/usr/bin/env python3
"""
Interactive Image Selection Manager for MagicScholar
Allows you to view all found images and select the best one manually
"""

import sys
from pathlib import Path
import logging
import requests
from PIL import Image
import io
import tempfile
import webbrowser
from typing import Dict, List, Any, Optional

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.services.enhanced_image_extractor import EnhancedImageExtractor
from app.models.institution import Institution

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InteractiveImageSelector:
    """Interactive image selection and management"""

    def __init__(self):
        self.db = SessionLocal()
        self.extractor = EnhancedImageExtractor(self.db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def debug_institution_images(self, institution_id: int):
        """Debug what images are found for a specific institution"""
        institution = (
            self.db.query(Institution)
            .filter(Institution.ipeds_id == institution_id)
            .first()
        )

        if not institution:
            logger.error(f"Institution {institution_id} not found")
            return

        logger.info("=" * 80)
        logger.info(f"DEBUGGING IMAGES FOR: {institution.name}")
        logger.info(f"Website: {institution.website}")
        logger.info("=" * 80)

        # Extract all images without uploading
        website = self.extractor.clean_url(institution.website)
        if not website:
            logger.error("No valid website URL")
            return

        try:
            # Get all images found on the website
            extracted_images = self.extractor.extract_enhanced_website_images(
                website, institution.name
            )

            if not extracted_images:
                logger.warning("No images found on website")
                return

            # Show all found images
            logger.info(f"Found {len(extracted_images)} images:")

            for idx, (img_type, img_data) in enumerate(extracted_images.items(), 1):
                logger.info(f"\n{idx}. Image Type: {img_type}")
                logger.info(f"   URL: {img_data['original_url']}")
                logger.info(f"   Quality Score: {img_data['quality_score']}")
                logger.info(
                    f"   Dimensions: {img_data['original_width']}x{img_data['original_height']}"
                )
                logger.info(f"   Size: {img_data['size_bytes']} bytes")

            # Show which would be selected automatically
            best_image = self.extractor.select_best_image(extracted_images)
            if best_image:
                logger.info(
                    f"\n🎯 AUTO-SELECTED: {best_image['image_type']} (Score: {best_image['quality_score']})"
                )
                logger.info(f"   URL: {best_image['original_url']}")

            return extracted_images

        except Exception as e:
            logger.error(f"Failed to extract images: {e}")
            return None

    def interactive_image_selection(self, institution_id: int):
        """Interactively select the best image for an institution"""
        institution = (
            self.db.query(Institution)
            .filter(Institution.ipeds_id == institution_id)
            .first()
        )

        if not institution:
            logger.error(f"Institution {institution_id} not found")
            return False

        logger.info("=" * 80)
        logger.info(f"INTERACTIVE IMAGE SELECTION: {institution.name}")
        logger.info("=" * 80)

        # Get all available images
        website = self.extractor.clean_url(institution.website)
        if not website:
            logger.error("No valid website URL")
            return False

        try:
            extracted_images = self.extractor.extract_enhanced_website_images(
                website, institution.name
            )

            if not extracted_images:
                logger.warning("No images found on website")
                return False

            # Show options
            logger.info("Available images:")
            image_list = list(extracted_images.items())

            for idx, (img_type, img_data) in enumerate(image_list, 1):
                logger.info(f"\n{idx}. {img_type.upper()}")
                logger.info(f"   Quality Score: {img_data['quality_score']}")
                logger.info(
                    f"   Dimensions: {img_data['original_width']}x{img_data['original_height']}"
                )
                logger.info(f"   URL: {img_data['original_url'][:80]}...")

            # Get user selection
            while True:
                try:
                    print("\nOptions:")
                    print(
                        "- Enter number (1-{}) to select an image".format(
                            len(image_list)
                        )
                    )
                    print("- Enter 'v' + number (e.g., 'v1') to view image in browser")
                    print("- Enter 'auto' to use automatic selection")
                    print("- Enter 'skip' to skip this institution")

                    choice = input("\nYour choice: ").strip().lower()

                    if choice == "skip":
                        logger.info("Skipping institution")
                        return False
                    elif choice == "auto":
                        best_image = self.extractor.select_best_image(extracted_images)
                        break
                    elif choice.startswith("v"):
                        # View image in browser
                        try:
                            img_num = int(choice[1:]) - 1
                            if 0 <= img_num < len(image_list):
                                img_url = image_list[img_num][1]["original_url"]
                                logger.info(f"Opening {img_url} in browser...")
                                webbrowser.open(img_url)
                            else:
                                print(f"Invalid number. Use 1-{len(image_list)}")
                        except ValueError:
                            print("Invalid format. Use 'v1', 'v2', etc.")
                        continue
                    else:
                        # Select by number
                        choice_num = int(choice) - 1
                        if 0 <= choice_num < len(image_list):
                            img_type, best_image = image_list[choice_num]
                            logger.info(
                                f"Selected: {img_type} (Score: {best_image['quality_score']})"
                            )
                            break
                        else:
                            print(f"Invalid choice. Use 1-{len(image_list)}")

                except ValueError:
                    print("Invalid input. Please try again.")

            # Upload the selected image
            if best_image:
                # Delete existing images first
                self.extractor.spaces_manager.delete_existing_images(institution.name)

                # Upload the selected image
                primary_url = self.extractor.upload_image_to_spaces(
                    best_image, "primary"
                )

                if primary_url:
                    # Update database
                    institution.primary_image_url = primary_url
                    institution.primary_image_quality_score = best_image[
                        "quality_score"
                    ]
                    institution.image_extraction_status = "SUCCESS"
                    self.db.commit()

                    logger.info(f"✅ Successfully updated {institution.name}")
                    logger.info(f"   URL: {primary_url}")
                    logger.info(f"   Quality Score: {best_image['quality_score']}")
                    return True
                else:
                    logger.error("Failed to upload image")
                    return False

        except Exception as e:
            logger.error(f"Interactive selection failed: {e}")
            return False

    def reprocess_with_options(self, institution_id: int):
        """Reprocess an institution and show all options"""
        logger.info("=" * 80)
        logger.info("REPROCESSING WITH ALL OPTIONS")
        logger.info("=" * 80)

        # First show debug info
        extracted_images = self.debug_institution_images(institution_id)

        if not extracted_images:
            return False

        # Then do interactive selection
        return self.interactive_image_selection(institution_id)

    def fix_problem_image(self, institution_name_or_id):
        """Fix a specific institution's problematic image"""
        try:
            # Try to find by IPEDS ID first
            if str(institution_name_or_id).isdigit():
                institution_id = int(institution_name_or_id)
            else:
                # Find by name
                institution = (
                    self.db.query(Institution)
                    .filter(Institution.name.ilike(f"%{institution_name_or_id}%"))
                    .first()
                )
                if not institution:
                    logger.error(f"Institution '{institution_name_or_id}' not found")
                    return False
                institution_id = institution.ipeds_id

            return self.reprocess_with_options(institution_id)

        except Exception as e:
            logger.error(f"Error fixing institution: {e}")
            return False

    def batch_review_mode(self, limit: int = 10):
        """Review multiple institutions interactively"""
        logger.info("=" * 80)
        logger.info(f"BATCH REVIEW MODE - {limit} institutions")
        logger.info("=" * 80)

        # Get institutions that need review (low quality scores or failed)
        problem_institutions = (
            self.db.query(Institution)
            .filter(
                (Institution.primary_image_quality_score < 60)
                | (Institution.image_extraction_status == "FAILED")
                | (Institution.primary_image_url.is_(None))
            )
            .filter(Institution.website.isnot(None))
            .limit(limit)
            .all()
        )

        if not problem_institutions:
            logger.info("No institutions found that need review!")
            return

        logger.info(f"Found {len(problem_institutions)} institutions to review")

        for idx, institution in enumerate(problem_institutions, 1):
            logger.info(
                f"\n[{idx}/{len(problem_institutions)}] Reviewing: {institution.name}"
            )

            current_score = institution.primary_image_quality_score or 0
            logger.info(f"Current quality score: {current_score}")

            if current_score > 0:
                logger.info(f"Current image: {institution.primary_image_url}")

            # Ask if user wants to reprocess this one
            choice = (
                input("Reprocess this institution? (y/n/q to quit): ").strip().lower()
            )

            if choice == "q":
                break
            elif choice == "y":
                success = self.reprocess_with_options(institution.ipeds_id)
                if success:
                    logger.info("✅ Successfully updated!")
                else:
                    logger.warning("❌ Update failed or skipped")
            else:
                logger.info("Skipping...")


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Image Selection Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Debug command
    debug_parser = subparsers.add_parser(
        "debug", help="Debug images for specific institution"
    )
    debug_parser.add_argument(
        "institution_id", type=int, help="IPEDS ID of institution"
    )

    # Fix command
    fix_parser = subparsers.add_parser(
        "fix", help="Fix problematic image for institution"
    )
    fix_parser.add_argument("institution", help="Institution name or IPEDS ID")

    # Review command
    review_parser = subparsers.add_parser("review", help="Batch review mode")
    review_parser.add_argument(
        "--limit", type=int, default=10, help="Number of institutions to review"
    )

    # Interactive command
    interactive_parser = subparsers.add_parser(
        "select", help="Interactive selection for institution"
    )
    interactive_parser.add_argument(
        "institution_id", type=int, help="IPEDS ID of institution"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        with InteractiveImageSelector() as selector:
            if args.command == "debug":
                selector.debug_institution_images(args.institution_id)
            elif args.command == "fix":
                selector.fix_problem_image(args.institution)
            elif args.command == "review":
                selector.batch_review_mode(args.limit)
            elif args.command == "select":
                selector.interactive_image_selection(args.institution_id)

    except KeyboardInterrupt:
        logger.info("\n⏹️  Operation cancelled by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
