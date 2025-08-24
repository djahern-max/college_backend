from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session  # Fixed: Use regular Session, not AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.oauth import OAuthState, OAuthAccount
from app.models.user import User
from app.core.config import settings
from app.core.security import create_access_token
from sqlalchemy import select
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()


@router.get("/google/url")
async def get_google_oauth_url(
    db: Session = Depends(get_db),
):  # Fixed: Session not AsyncSession
    """Generate Google OAuth authorization URL"""

    # Generate secure state parameter
    state = secrets.token_urlsafe(32)

    # Store state in database for verification
    oauth_state = OAuthState(
        state=state,
        provider="google",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(oauth_state)
    db.commit()  # Fixed: removed await

    # Build authorization URL
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
        params
    )

    return {"url": auth_url, "state": state}


@router.get("/linkedin/url")
async def get_linkedin_oauth_url(db: Session = Depends(get_db)):
    """Generate LinkedIn OAuth authorization URL"""

    # Generate secure state parameter
    state = secrets.token_urlsafe(32)

    # Store state in database for verification
    oauth_state = OAuthState(
        state=state,
        provider="linkedin",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(oauth_state)
    db.commit()  # Fixed: removed await

    # Build authorization URL
    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "scope": "r_liteprofile r_emailaddress",
        "state": state,
    }

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urllib.parse.urlencode(params)
    )
    return {"url": auth_url, "state": state}


@router.get("/tiktok/url")
async def get_tiktok_oauth_url(db: Session = Depends(get_db)):
    """Generate TikTok OAuth authorization URL"""

    # Generate secure state parameter
    state = secrets.token_urlsafe(32)

    # Store state in database for verification
    oauth_state = OAuthState(
        state=state,
        provider="tiktok",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(oauth_state)
    db.commit()  # Fixed: removed await

    # Build authorization URL
    params = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "scope": "user.info.basic",
        "response_type": "code",
        "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        "state": state,
    }

    auth_url = "https://www.tiktok.com/auth/authorize/?" + urllib.parse.urlencode(
        params
    )
    return {"url": auth_url, "state": state}


# Simplified callback endpoints for testing
@router.get("/google/callback")
async def google_oauth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Google OAuth callback"""
    return {"message": "Google OAuth callback received", "code": code, "state": state}


@router.get("/linkedin/callback")
async def linkedin_oauth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle LinkedIn OAuth callback"""
    return {"message": "LinkedIn OAuth callback received", "code": code, "state": state}


@router.get("/tiktok/callback")
async def tiktok_oauth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle TikTok OAuth callback"""
    return {"message": "TikTok OAuth callback received", "code": code, "state": state}


@router.get("/accounts")
async def get_oauth_accounts(current_user: dict = Depends(get_current_user)):
    """Get connected OAuth accounts"""
    return {"oauth_accounts": []}


@router.delete("/accounts/{provider}")
async def disconnect_oauth_account(
    provider: str, current_user: dict = Depends(get_current_user)
):
    """Disconnect OAuth account"""
    return {"message": f"{provider} account disconnected"}
