from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.oauth import OAuthService
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
oauth_service = OAuthService()


@router.get("/google/url")
async def get_google_oauth_url(db: AsyncSession = Depends(get_db)):
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
    await db.commit()

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
async def get_linkedin_oauth_url(db: AsyncSession = Depends(get_db)):
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
    await db.commit()

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
async def get_tiktok_oauth_url(db: AsyncSession = Depends(get_db)):
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
    await db.commit()

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


@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""

    # Verify state parameter
    result = await db.execute(
        select(OAuthState).where(
            OAuthState.state == state,
            OAuthState.provider == "google",
            OAuthState.expires_at > datetime.utcnow(),
        )
    )
    oauth_state = result.scalar_one_or_none()

    if not oauth_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    try:
        # Handle OAuth callback
        result = await oauth_service.handle_google_callback(code, db)
        user = result["user"]

        # Create access token
        access_token = create_access_token(data={"sub": user.username})

        # Clean up state
        await db.delete(oauth_state)
        await db.commit()

        # Redirect to frontend with token
        frontend_url = f"{settings.FRONTEND_URL}/auth/success?token={access_token}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        # Clean up state on error
        await db.delete(oauth_state)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}",
        )


@router.get("/linkedin/callback")
async def linkedin_oauth_callback(
    code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)
):
    """Handle LinkedIn OAuth callback"""

    # Verify state parameter
    result = await db.execute(
        select(OAuthState).where(
            OAuthState.state == state,
            OAuthState.provider == "linkedin",
            OAuthState.expires_at > datetime.utcnow(),
        )
    )
    oauth_state = result.scalar_one_or_none()

    if not oauth_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    try:
        # Handle OAuth callback
        result = await oauth_service.handle_linkedin_callback(code, db)
        user = result["user"]

        # Create access token
        access_token = create_access_token(data={"sub": user.username})

        # Clean up state
        await db.delete(oauth_state)
        await db.commit()

        # Redirect to frontend with token
        frontend_url = f"{settings.FRONTEND_URL}/auth/success?token={access_token}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        # Clean up state on error
        await db.delete(oauth_state)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}",
        )


@router.get("/tiktok/callback")
async def tiktok_oauth_callback(
    code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)
):
    """Handle TikTok OAuth callback"""

    # Verify state parameter
    result = await db.execute(
        select(OAuthState).where(
            OAuthState.state == state,
            OAuthState.provider == "tiktok",
            OAuthState.expires_at > datetime.utcnow(),
        )
    )
    oauth_state = result.scalar_one_or_none()

    if not oauth_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    try:
        # Handle OAuth callback
        result = await oauth_service.handle_tiktok_callback(code, db)
        user = result["user"]

        # Create access token
        access_token = create_access_token(data={"sub": user.username})

        # Clean up state
        await db.delete(oauth_state)
        await db.commit()

        # Redirect to frontend with token
        frontend_url = f"{settings.FRONTEND_URL}/auth/success?token={access_token}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        # Clean up state on error
        await db.delete(oauth_state)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}",
        )


@router.get("/accounts")
async def get_oauth_accounts(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get connected OAuth accounts for current user"""

    result = await db.execute(
        select(OAuthAccount).where(OAuthAccount.user_id == current_user.id)
    )
    oauth_accounts = result.scalars().all()

    # Return account info without sensitive data
    accounts = []
    for account in oauth_accounts:
        accounts.append(
            {
                "provider": account.provider,
                "email": account.email,
                "connected_at": account.created_at,
                "profile_data": {
                    k: v
                    for k, v in account.profile_data.items()
                    if k in ["name", "display_name", "given_name", "family_name"]
                },
            }
        )

    return {"oauth_accounts": accounts}


@router.delete("/accounts/{provider}")
async def disconnect_oauth_account(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect OAuth account"""

    if provider not in ["google", "linkedin", "tiktok"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth provider"
        )

    result = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.user_id == current_user.id, OAuthAccount.provider == provider
        )
    )
    oauth_account = result.scalar_one_or_none()

    if not oauth_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {provider} account connected",
        )

    await db.delete(oauth_account)
    await db.commit()

    return {"message": f"{provider.title()} account disconnected successfully"}
