"""
Review service for business logic.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    """Service class for review operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, review_data: ReviewCreate) -> Review:
        """Create a new review."""
        review = Review(
            user_id=user_id,
            **review_data.model_dump()
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_by_id(self, review_id: int) -> Optional[Review]:
        """Get review by ID."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def get_user_review(self, user_id: int) -> Optional[Review]:
        """Get review by user (one review per user)."""
        result = await self.db.execute(
            select(Review).where(Review.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_reviews(self, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get all reviews with pagination."""
        result = await self.db.execute(
            select(Review)
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(self, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
        """Update a review."""
        review = await self.get_by_id(review_id)
        if not review:
            return None

        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review_id: int) -> bool:
        """Delete a review."""
        review = await self.get_by_id(review_id)
        if not review:
            return False

        await self.db.delete(review)
        await self.db.commit()
        return True

    async def get_statistics(self) -> dict:
        """Get review statistics."""
        # Get total count and average rating
        result = await self.db.execute(
            select(
                func.count(Review.id).label('total_reviews'),
                func.avg(Review.rating).label('average_rating')
            )
        )
        stats = result.first()
        
        total_reviews = stats.total_reviews or 0
        average_rating = float(stats.average_rating or 0.0)

        # Get rating distribution
        rating_dist_result = await self.db.execute(
            select(
                Review.rating,
                func.count(Review.id).label('count')
            ).group_by(Review.rating).order_by(Review.rating)
        )
        
        rating_distribution = {row.rating: row.count for row in rating_dist_result}

        return {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 1),
            'rating_distribution': rating_distribution
        }