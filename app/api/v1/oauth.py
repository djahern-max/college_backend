from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/google/url")
async def get_google_oauth_url():
    """Get Google OAuth URL"""
    return {
        "url": "https://accounts.google.com/oauth/authorize?...",
        "state": "test_state_123"
    }


@router.get("/linkedin/url")
async def get_linkedin_oauth_url():
    """Get LinkedIn OAuth URL"""
    return {
        "url": "https://www.linkedin.com/oauth/v2/authorization?...",
        "state": "test_state_456"
    }


@router.get("/tiktok/url")
async def get_tiktok_oauth_url():
    """Get TikTok OAuth URL"""
    return {
        "url": "https://www.tiktok.com/auth/authorize?...",
        "state": "test_state_789"
    }


@router.get("/google/callback")
async def google_oauth_callback():
    """Handle Google OAuth callback"""
    return {"message": "Google OAuth callback working"}


@router.get("/linkedin/callback")
async def linkedin_oauth_callback():
    """Handle LinkedIn OAuth callback"""
    return {"message": "LinkedIn OAuth callback working"}


@router.get("/tiktok/callback")
async def tiktok_oauth_callback():
    """Handle TikTok OAuth callback"""
    return {"message": "TikTok OAuth callback working"}


@router.get("/accounts")
async def get_oauth_accounts(current_user: dict = Depends(get_current_user)):
    """Get connected OAuth accounts"""
    return {"oauth_accounts": []}


@router.delete("/accounts/{provider}")
async def disconnect_oauth_account(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Disconnect OAuth account"""
    return {"message": f"{provider} account disconnected"}
