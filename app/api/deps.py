from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.database import get_db

security = HTTPBearer()

async def get_current_user():
    """Simplified current user dependency for testing"""
    # For now, return a mock user
    return {"id": 1, "username": "test_user", "email": "test@example.com"}
