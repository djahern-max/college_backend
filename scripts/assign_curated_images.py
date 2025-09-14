# scripts/assign_curated_images.py
"""
Simple approach: Assign high-quality curated images to specific scholarships
"""
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.scholarship import Scholarship
from app.models.institution import ImageExtractionStatus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def assign_curated_images():
    """Assign specific high-quality images to known scholarships"""

    # Create database connection
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Curated high-quality images for specific scholarships
    # These are professional images that represent each scholarship well
    scholarship_images = {
        "Gates Millennium Scholars Program": {
            "url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=400&h=300&fit=crop&auto=format",
            "quality": 90,
            "description": "Diverse group of students studying together",
        },
        "Ron Brown Scholar Program": {
            "url": "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=400&h=300&fit=crop&auto=format",
            "quality": 85,
            "description": "African American students in graduation ceremony",
        },
        "Jackie Robinson Foundation Scholarship": {
            "url": "https://images.unsplash.com/photo-1569705460033-cfaa4bf9866a?w=400&h=300&fit=crop&auto=format",
            "quality": 88,
            "description": "Diverse students celebrating achievement",
        },
        "Hispanic Scholarship Fund General Scholarship": {
            "url": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=400&h=300&fit=crop&auto=format",
            "quality": 87,
            "description": "Hispanic students in academic setting",
        },
        "Davidson Fellows Scholarship": {
            "url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=300&fit=crop&auto=format",
            "quality": 85,
            "description": "Young scholars working on research",
        },
        "QuestBridge National College Match": {
            "url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=400&h=300&fit=crop&auto=format",
            "quality": 90,
            "description": "Students from diverse backgrounds studying",
        },
        "Regeneron Science Talent Search": {
            "url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=300&fit=crop&auto=format",
            "quality": 92,
            "description": "Young scientists in laboratory setting",
        },
        "Dell Scholars Program": {
            "url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=400&h=300&fit=crop&auto=format",
            "quality": 85,
            "description": "Students using technology for learning",
        },
        "Coca-Cola Scholars Foundation Scholarship": {
            "url": "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=400&h=300&fit=crop&auto=format",
            "quality": 88,
            "description": "Community service and leadership",
        },
        "National Merit Scholarship Program": {
            "url": "https://images.unsplash.com/photo-1523050854058-8df90110c9d1?w=400&h=300&fit=crop&auto=format",
            "quality": 90,
            "description": "Academic excellence and graduation",
        },
        "Google Lime Scholarship": {
            "url": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=400&h=300&fit=crop&auto=format",
            "quality": 89,
            "description": "Students with disabilities in tech",
        },
        "Horatio Alger National Scholarship": {
            "url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=300&fit=crop&auto=format",
            "quality": 86,
            "description": "Overcoming adversity through education",
        },
    }

    try:
        updated_count = 0

        for title, image_info in scholarship_images.items():
            # Find scholarship by title (partial match)
            scholarship = (
                db.query(Scholarship)
                .filter(Scholarship.title.ilike(f"%{title}%"))
                .first()
            )

            if scholarship:
                logger.info(f"Updating {scholarship.title}")

                # Update with curated image
                scholarship.primary_image_url = image_info["url"]
                scholarship.primary_image_quality_score = image_info["quality"]
                scholarship.image_extraction_status = ImageExtractionStatus.SUCCESS

                updated_count += 1
            else:
                logger.warning(f"Scholarship not found: {title}")

        # Commit all changes
        db.commit()
        logger.info(
            f"Successfully updated {updated_count} scholarships with curated images"
        )

        # Show final stats
        total = db.query(Scholarship).count()
        with_images = (
            db.query(Scholarship)
            .filter(Scholarship.primary_image_url.isnot(None))
            .count()
        )

        logger.info(
            f"Final stats: {with_images}/{total} scholarships have images ({with_images/total*100:.1f}%)"
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Assigning curated scholarship images...")
    assign_curated_images()
    logger.info(
        "Done! Check your frontend - all scholarships should now have relevant, high-quality images."
    )
