"""
Review endpoints for platform feedback.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies.auth import get_current_active_user, get_optional_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.services.review import ReviewService

router = APIRouter()


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new review (one per user)."""
    review_service = ReviewService(db)
    
    # Check if user already has a review
    existing_review = await review_service.get_user_review(current_user.id)
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a review. You can update your existing review instead."
        )
    
    review = await review_service.create(current_user.id, review_data)
    
    # Return response with user name
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user_name=current_user.first_name or current_user.username
    )


@router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews with pagination."""
    review_service = ReviewService(db)
    reviews = await review_service.get_reviews(skip=skip, limit=limit)
    
    return [
        ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_name=review.user.first_name or review.user.username if review.user else "Anonymous"
        )
        for review in reviews
    ]


@router.get("/reviews/my", response_model=ReviewResponse)
async def get_my_review(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's review."""
    review_service = ReviewService(db)
    review = await review_service.get_user_review(current_user.id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't submitted a review yet"
        )
    
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user_name=current_user.first_name or current_user.username
    )


@router.put("/reviews/my", response_model=ReviewResponse)
async def update_my_review(
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's review."""
    review_service = ReviewService(db)
    review = await review_service.get_user_review(current_user.id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't submitted a review yet"
        )
    
    updated_review = await review_service.update(review.id, review_data)
    
    return ReviewResponse(
        id=updated_review.id,
        user_id=updated_review.user_id,
        rating=updated_review.rating,
        title=updated_review.title,
        comment=updated_review.comment,
        created_at=updated_review.created_at,
        updated_at=updated_review.updated_at,
        user_name=current_user.first_name or current_user.username
    )


@router.delete("/reviews/my", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_review(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user's review."""
    review_service = ReviewService(db)
    review = await review_service.get_user_review(current_user.id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't submitted a review yet"
        )
    
    await review_service.delete(review.id)


@router.get("/reviews/statistics")
async def get_review_statistics(db: AsyncSession = Depends(get_db)):
    """Get review statistics."""
    review_service = ReviewService(db)
    return await review_service.get_statistics()