# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import jwt
from app.core.config import settings
from app.services.user import UserService
from jose import JWTError
import logging

logger = logging.getLogger("auth")
security = HTTPBearer()


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token, return the full payload.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error("JWT verification failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(security), db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    try:
        # Extract the actual token from the HTTPAuthorizationCredentials
        if hasattr(token, "credentials"):
            token_str = token.credentials
        else:
            token_str = str(token)

        logger.info(
            "Verifying token: %s",
            token_str[:20] + "..." if len(token_str) > 20 else token_str,
        )

        # Verify the JWT token and get payload
        payload = verify_token(token_str)
        user_id = payload.get("sub")

        if not user_id:
            logger.error("No user ID found in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user_service = UserService(db)
        user = user_service.get_by_id(int(user_id))

        if not user:
            logger.error("User not found for ID: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.error("User is not active: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info("Successfully authenticated user: %s", user.email)

        # CHANGED: Return the actual User object instead of dict
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Token verification failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
