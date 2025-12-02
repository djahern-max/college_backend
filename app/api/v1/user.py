# app/api/v1/user.py - SYNC VERSION
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.services.user import UserService
from app.schemas.auth import LoginResponse, LoginRequest
from app.schemas.user import UserResponse, UserCreate
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
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
    return UserResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login with email and password (OAuth2 form format)"""
    user_service = UserService(db)

    user = user_service.authenticate(form_data.username, form_data.password)
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

    user_service.update_last_login(user.id)

    # Create access token using user ID
    access_token = create_access_token(subject=user.id)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800,
        user=UserResponse.model_validate(user).model_dump(),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user info"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout():
    """Logout endpoint"""
    # In a more complex setup, you might invalidate the token here
    # For now, logout is handled client-side by removing the token
    return {"message": "Logout successful"}
