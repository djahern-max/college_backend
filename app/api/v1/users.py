from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user_service = UserService(db)

    # Check if email already exists
    if user_service.is_email_taken(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username already exists
    if user_service.is_username_taken(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create the user
    user = user_service.create_user(user_data)
    return UserResponse.from_orm(user)


@router.get("/me", response_model=UserResponse)
async def get_my_user_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's information"""
    user_service = UserService(db)
    user = user_service.get_by_id(current_user["id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.from_orm(user)


@router.patch("/me", response_model=UserResponse)
async def update_my_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's information"""
    user_service = UserService(db)

    # Check if trying to update email to one that already exists
    if user_update.email and user_service.is_email_taken(
        user_update.email, exclude_user_id=current_user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
        )

    # Check if trying to update username to one that already exists
    if user_update.username and user_service.is_username_taken(
        user_update.username, exclude_user_id=current_user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    user = user_service.update_user(current_user["id"], user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.from_orm(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user by ID"""
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.from_orm(user)
