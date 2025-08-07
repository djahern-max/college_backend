"""
Authentication endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse
from app.schemas.user import UserResponse
from app.services.user import UserService
from app.core.security.jwt import create_access_token
from app.core.config.settings import get_settings
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
settings = get_settings()


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint to authenticate user and return JWT token.
    """
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Prepare user data for response (exclude sensitive information)
    user_data = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user_data
    )


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout endpoint. Since we're using stateless JWT tokens,
    this endpoint primarily serves to validate the token and 
    confirm logout on the client side.
    
    In a production environment, you might want to:
    1. Add the token to a blacklist/revocation list
    2. Store blacklisted tokens in Redis with expiration
    3. Check blacklist in token verification
    """
    return LogoutResponse(message="Successfully logged out")


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.post("/auth/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Refresh access token for authenticated user.
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }