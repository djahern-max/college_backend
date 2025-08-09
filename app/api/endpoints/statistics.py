"""
Statistics endpoints for platform metrics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter()

@router.get("/statistics/platform")
async def get_platform_statistics(db: AsyncSession = Depends(get_db)):
    """Get platform-wide statistics."""
    
    # Get user count
    user_count_result = await db.execute(text("SELECT COUNT(*) FROM users"))
    user_count = user_count_result.scalar() or 0
    
    # Get scholarship count
    scholarship_count_result = await db.execute(text("SELECT COUNT(*) FROM scholarships WHERE verified = true"))
    scholarship_count = scholarship_count_result.scalar() or 0
    
    # Calculate total amounts
    amount_result = await db.execute(text("""
        SELECT 
            SUM(
                CASE
                    WHEN amount_exact IS NOT NULL THEN amount_exact
                    WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN (amount_min + amount_max) / 2.0
                    WHEN amount_min IS NOT NULL THEN amount_min
                    WHEN amount_max IS NOT NULL THEN amount_max
                    ELSE 0
                END
            ) as total_amount
        FROM scholarships
        WHERE verified = true
    """))
    
    total_amount = amount_result.scalar() or 0.0
    total_amount = float(total_amount)
    
    # Get review statistics and count "students helped" as users with 4+ star reviews
    try:
        review_stats_result = await db.execute(text("""
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as average_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as students_helped
            FROM reviews
        """))
        
        review_data = review_stats_result.fetchone()
        total_reviews = review_data[0] if review_data[0] else 0
        average_rating = float(review_data[1]) if review_data[1] else 0.0
        students_helped = review_data[2] if review_data[2] else 0
        
    except Exception as e:
        # If reviews table doesn't exist or has issues, default to 0
        print(f"Review stats error: {e}")
        total_reviews = 0
        average_rating = 0.0
        students_helped = 0
    
    # Format display text for reviews
    if total_reviews == 0:
        rating_display = "No reviews yet"
    else:
        rating_display = f"{average_rating:.1f}/5 from {total_reviews:,} student{'s' if total_reviews != 1 else ''}"
    
    # Format total amount for display (without decimals)
    def format_amount(amount):
        if amount >= 1_000_000_000:
            return f"${amount/1_000_000_000:.0f}B+"
        elif amount >= 1_000_000:
            return f"${amount/1_000_000:.0f}M+"
        elif amount >= 1_000:
            return f"${amount/1_000:.0f}K+"
        else:
            return f"${amount:,.0f}+"
    
    return {
        "total_users": user_count,
        "total_scholarships": scholarship_count,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "rating_display": rating_display,
        "total_scholarship_amount": total_amount,
        "formatted_scholarship_amount": format_amount(total_amount),
        "students_helped": students_helped  # New field for 4+ star reviews
    }