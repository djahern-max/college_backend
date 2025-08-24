from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/google/url")
def get_google_oauth_url(db: Session = Depends(get_db)):
    import logging
    import secrets
    import urllib.parse
    from datetime import datetime, timedelta
    from app.core.config import settings

    logger = logging.getLogger("oauth")

    try:
        # 1) Generate state
        state = secrets.token_urlsafe(32)
        logger.info("Generating OAuth state %s", state[:8])

        # 2) Sanity-check config (soft-fail logging)
        logger.info("GOOGLE_CLIENT_ID set? %s", bool(settings.GOOGLE_CLIENT_ID))
        logger.info("GOOGLE_REDIRECT_URI: %s", settings.GOOGLE_REDIRECT_URI)

        # 3) Persist state
        from app.models.oauth import OAuthState

        oauth_state = OAuthState(
            state=state,
            provider="google",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(oauth_state)
        db.commit()
        db.refresh(oauth_state)
        logger.info("OAuthState committed for provider=google")

        # 4) Build URL
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode(params)
        )
        return {"url": auth_url, "state": state}

    except Exception as e:
        logger.exception("Failed to build Google OAuth URL")
        raise HTTPException(
            status_code=500, detail=f"/google/url failed: {type(e).__name__}: {e}"
        )


@router.get("/linkedin/url")
def get_linkedin_oauth_url():
    """Get LinkedIn OAuth URL"""
    return {
        "url": "https://www.linkedin.com/oauth/v2/authorization?...",
        "state": "test_state_456",
    }


@router.get("/tiktok/url")
def get_tiktok_oauth_url():
    """Get TikTok OAuth URL"""
    return {
        "url": "https://www.tiktok.com/auth/authorize?...",
        "state": "test_state_789",
    }


@router.get("/google/callback")
def google_oauth_callback():
    """Handle Google OAuth callback"""
    return {"message": "Google OAuth callback working"}


@router.get("/linkedin/callback")
def linkedin_oauth_callback():
    """Handle LinkedIn OAuth callback"""
    return {"message": "LinkedIn OAuth callback working"}


@router.get("/tiktok/callback")
def tiktok_oauth_callback():
    """Handle TikTok OAuth callback"""
    return {"message": "TikTok OAuth callback working"}


@router.get("/accounts")
def get_oauth_accounts(current_user: dict = Depends(get_current_user)):
    """Get connected OAuth accounts"""
    return {"oauth_accounts": []}


@router.delete("/accounts/{provider}")
def disconnect_oauth_account(
    provider: str, current_user: dict = Depends(get_current_user)
):
    """Disconnect OAuth account"""
    return {"message": f"{provider} account disconnected"}
