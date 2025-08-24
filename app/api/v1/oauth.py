from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
import logging
import secrets
import urllib.parse
import httpx
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.oauth import OAuthState, OAuthAccount
from app.models.user import User
from app.core.security import create_access_token
from app.services.user import UserService
from app.schemas.user import UserCreate

router = APIRouter()
logger = logging.getLogger("oauth")


@router.get("/google/url")
def get_google_oauth_url(db: Session = Depends(get_db)):
    try:
        # 1) Generate state
        state = secrets.token_urlsafe(32)
        logger.info("Generating OAuth state %s", state[:8])

        # 2) Sanity-check config (soft-fail logging)
        logger.info("GOOGLE_CLIENT_ID set? %s", bool(settings.GOOGLE_CLIENT_ID))
        logger.info("GOOGLE_REDIRECT_URI: %s", settings.GOOGLE_REDIRECT_URI)

        # 3) Persist state
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


@router.get("/google/callback")
def google_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        logger.info("OAuth callback received - code: %s, state: %s", code[:10] + "..." if code else "None", state[:8] + "..." if state else "None")
        
        # 1) Verify state
        oauth_state = db.query(OAuthState).filter(
            OAuthState.state == state,
            OAuthState.provider == "google",
            OAuthState.used.is_not(True),  # Allow both NULL and False values
            OAuthState.expires_at > datetime.utcnow()
        ).first()
        
        if not oauth_state:
            # Add debug info about why state verification failed
            all_states = db.query(OAuthState).filter(OAuthState.state == state).all()
            logger.error("State verification failed for: %s", state[:8])
            logger.error("States found with this value: %d", len(all_states))
            for s in all_states:
                logger.error("State details - provider: %s, used: %s, expired: %s", 
                           s.provider, s.used, s.expires_at < datetime.utcnow())
            
            error_url = f"{settings.FRONTEND_URL}/auth/error?message=invalid_state"
            return RedirectResponse(url=error_url)
        
        # 2) Mark state as used
        oauth_state.used = True
        db.commit()
        logger.info("OAuth state marked as used: %s", state[:8])
        
        # 3) Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }
        
        logger.info("Exchanging authorization code for access token")
        with httpx.Client() as client:
            token_response = client.post(token_url, data=token_data, timeout=10.0)
            token_response.raise_for_status()
            tokens = token_response.json()
        logger.info("Successfully received tokens from Google")
        
        # 4) Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        with httpx.Client() as client:
            user_response = client.get(user_info_url, headers=headers, timeout=10.0)
            user_response.raise_for_status()
            user_data = user_response.json()
        
        logger.info("Google user data received for: %s", user_data.get('email', 'unknown'))
        
        # 5) Find or create user account
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == "google",
            OAuthAccount.provider_user_id == user_data['id']
        ).first()
        
        if oauth_account:
            # Existing OAuth account - update tokens
            logger.info("Updating existing OAuth account for user: %s", oauth_account.user_id)
            oauth_account.access_token = tokens['access_token']
            oauth_account.refresh_token = tokens.get('refresh_token')
            oauth_account.profile_data = user_data
            oauth_account.updated_at = datetime.utcnow()
            user = oauth_account.user
        else:
            # Check if user exists by email
            user = db.query(User).filter(User.email == user_data['email']).first()
            
            if not user:
                # Create new user
                logger.info("Creating new user account for: %s", user_data.get('email'))
                user_service = UserService(db)
                
                # Generate a unique username based on email
                base_username = user_data['email'].split('@')[0]
                username = base_username
                counter = 1
                while user_service.is_username_taken(username):
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user_create = UserCreate(
                    email=user_data['email'],
                    username=username,
                    first_name=user_data.get('given_name', ''),
                    last_name=user_data.get('family_name', ''),
                    password="oauth_user_no_password"  # OAuth users don't need passwords
                )
                user = user_service.create_user(user_create)
                logger.info("Created new user with ID: %s", user.id)
            else:
                logger.info("Linking OAuth account to existing user: %s", user.id)
            
            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_user_id=user_data['id'],
                email=user_data['email'],
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                profile_data=user_data,
                created_at=datetime.utcnow()
            )
            db.add(oauth_account)
        
        db.commit()
        logger.info("OAuth account setup completed for user: %s", user.id)
        
        # 6) Create JWT token for the user
        access_token = create_access_token(subject=user.id)
        logger.info("JWT token created for user: %s", user.id)
        
        # 7) Redirect to frontend auth callback page with token
        callback_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        logger.info("Redirecting to frontend callback: %s", callback_url.split('?')[0])
        return RedirectResponse(url=callback_url)
        
    except httpx.RequestError as e:
        logger.exception("HTTP request failed during OAuth callback: %s", str(e))
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=oauth_failed"
        return RedirectResponse(url=error_url)
    except Exception as e:
        logger.exception("OAuth callback failed: %s", str(e))
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=oauth_failed"
        return RedirectResponse(url=error_url)


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