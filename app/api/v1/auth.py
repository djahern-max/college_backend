from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.services.user import UserService
from app.schemas.auth import LoginResponse, LoginRequest
from app.schemas.user import UserResponse, UserCreate
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
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


@router.post("/login", response_model=LoginResponse)
async def login_for_access_token(
    login_data: LoginRequest,  # Use your custom schema instead
    db: Session = Depends(get_db),
):
    """Login with email and password"""
    user_service = UserService(db)

    # Now it's clear - using email
    user = user_service.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Update last login timestamp
    user_service.update_last_login(user.id)

    # Create access token using user ID
    access_token = create_access_token(subject=user.id)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
        user=UserResponse.from_orm(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user info"""
    user_service = UserService(db)
    user = user_service.get_by_id(current_user["id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.from_orm(user)


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    # In a more complex setup, you might invalidate the token here
    # For now, logout is handled client-side by removing the token
    return {"message": "Logout successful"}
