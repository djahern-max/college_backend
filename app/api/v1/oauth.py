from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
import logging
import secrets
import urllib.parse
import httpx
from datetime import datetime, timedelta, timezone
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
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
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
        logger.info(
            "OAuth callback received - code: %s, state: %s",
            code[:10] + "..." if code else "None",
            state[:8] + "..." if state else "None",
        )

        # 1) Verify state
        oauth_state = (
            db.query(OAuthState)
            .filter(
                OAuthState.state == state,
                OAuthState.provider == "google",
                OAuthState.used.is_not(True),
                OAuthState.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

        if not oauth_state:
            # Add debug info about why state verification failed
            all_states = db.query(OAuthState).filter(OAuthState.state == state).all()
            logger.error("State verification failed for: %s", state[:8])
            logger.error("States found with this value: %d", len(all_states))
            for s in all_states:
                logger.error(
                    "State details - provider: %s, used: %s, expired: %s",
                    s.provider,
                    s.used,
                    s.expires_at < datetime.now(timezone.utc),
                )

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
        logger.info(
            "Token request data - client_id: %s, redirect_uri: %s",
            settings.GOOGLE_CLIENT_ID[:20] + "...",
            settings.GOOGLE_REDIRECT_URI,
        )

        with httpx.Client() as client:
            token_response = client.post(token_url, data=token_data, timeout=10.0)
            logger.info("Token response status: %d", token_response.status_code)
            if token_response.status_code != 200:
                logger.error("Token response error: %s", token_response.text)
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

        logger.info(
            "Google user data received for: %s", user_data.get("email", "unknown")
        )

        # 5) Find or create user account
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == "google",
                OAuthAccount.provider_user_id == user_data["id"],
            )
            .first()
        )

        if oauth_account:
            # Existing OAuth account - update tokens
            logger.info(
                "Updating existing OAuth account for user: %s", oauth_account.user_id
            )
            oauth_account.access_token = tokens["access_token"]
            oauth_account.refresh_token = tokens.get("refresh_token")
            oauth_account.profile_data = user_data
            oauth_account.updated_at = datetime.now(timezone.utc)
            user = oauth_account.user
        else:
            # Check if user exists by email
            user = db.query(User).filter(User.email == user_data["email"]).first()

            if not user:
                # Create new user
                logger.info("Creating new user account for: %s", user_data.get("email"))
                user_service = UserService(db)

                # Generate a unique username based on email
                base_username = user_data["email"].split("@")[0]
                base_username = "".join(
                    c if c.isalnum() or c in "_-" else "_" for c in base_username
                )
                if base_username and not base_username[0].isalnum():
                    base_username = "user_" + base_username
                if not base_username:
                    base_username = "oauth_user"

                username = base_username
                counter = 1
                while user_service.is_username_taken(username):
                    username = f"{base_username}{counter}"
                    counter += 1

                user_create = UserCreate(
                    email=user_data["email"],
                    username=username,
                    first_name=user_data.get("given_name", ""),
                    last_name=user_data.get("family_name", ""),
                    password="oauth_user_no_password",
                )
                user = user_service.create_user(user_create)
                logger.info("Created new user with ID: %s", user.id)
            else:
                logger.info("Linking OAuth account to existing user: %s", user.id)

            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_user_id=user_data["id"],
                email=user_data["email"],
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                profile_data=user_data,
                created_at=datetime.now(timezone.utc),
            )
            db.add(oauth_account)

        db.commit()
        logger.info("OAuth account setup completed for user: %s", user.id)

        # 6) Create JWT token for the user
        access_token = create_access_token(subject=user.id)
        logger.info("JWT token created for user: %s", user.id)

        # 7) Redirect to frontend auth callback page with token
        newly_created_user = (
            not oauth_account
            or oauth_account.created_at
            >= datetime.now(timezone.utc) - timedelta(minutes=5)
        )

        if newly_created_user:
            callback_url = (
                f"{settings.FRONTEND_URL}/callback?token={access_token}&new_user=true"
            )
        else:
            callback_url = f"{settings.FRONTEND_URL}/callback?token={access_token}"

        logger.info("Redirecting to frontend callback: %s", callback_url.split("?")[0])
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
def get_linkedin_oauth_url(db: Session = Depends(get_db)):
    try:
        state = secrets.token_urlsafe(32)
        logger.info("Generating LinkedIn OAuth state %s", state[:8])

        logger.info("LINKEDIN_CLIENT_ID set? %s", bool(settings.LINKEDIN_CLIENT_ID))
        logger.info("LINKEDIN_REDIRECT_URI: %s", settings.LINKEDIN_REDIRECT_URI)

        oauth_state = OAuthState(
            state=state,
            provider="linkedin",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        db.add(oauth_state)
        db.commit()
        db.refresh(oauth_state)
        logger.info("OAuthState committed for provider=linkedin")

        params = {
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
        }
        auth_url = (
            "https://www.linkedin.com/oauth/v2/authorization?"
            + urllib.parse.urlencode(params)
        )
        return {"url": auth_url, "state": state}

    except Exception as e:
        logger.exception("Failed to build LinkedIn OAuth URL")
        raise HTTPException(
            status_code=500, detail=f"/linkedin/url failed: {type(e).__name__}: {e}"
        )


@router.get("/linkedin/callback")
def linkedin_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle LinkedIn OAuth callback"""
    try:
        logger.info(
            "LinkedIn OAuth callback received - code: %s, state: %s",
            code[:10] + "..." if code else "None",
            state[:8] + "..." if state else "None",
        )

        oauth_state = (
            db.query(OAuthState)
            .filter(
                OAuthState.state == state,
                OAuthState.provider == "linkedin",
                OAuthState.used.is_not(True),
                OAuthState.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

        if not oauth_state:
            logger.error("LinkedIn state verification failed for: %s", state[:8])
            error_url = f"{settings.FRONTEND_URL}/auth/error?message=invalid_state"
            return RedirectResponse(url=error_url)

        oauth_state.used = True
        db.commit()
        logger.info("LinkedIn OAuth state marked as used: %s", state[:8])

        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        }

        logger.info("Exchanging LinkedIn authorization code for access token")

        with httpx.Client() as client:
            token_response = client.post(
                token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
            logger.info(
                "LinkedIn token response status: %d", token_response.status_code
            )
            if token_response.status_code != 200:
                logger.error("LinkedIn token response error: %s", token_response.text)
                token_response.raise_for_status()
            tokens = token_response.json()

        logger.info("Successfully received tokens from LinkedIn")

        profile_url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        with httpx.Client() as client:
            profile_response = client.get(profile_url, headers=headers, timeout=10.0)
            profile_response.raise_for_status()
            userinfo_data = profile_response.json()

        user_data = {
            "id": userinfo_data["sub"],
            "email": userinfo_data["email"],
            "given_name": userinfo_data.get("given_name", ""),
            "family_name": userinfo_data.get("family_name", ""),
            "name": userinfo_data.get(
                "name",
                f"{userinfo_data.get('given_name', '')} {userinfo_data.get('family_name', '')}",
            ).strip(),
        }

        logger.info(
            "LinkedIn user data received for: %s", user_data.get("email", "unknown")
        )

        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == "linkedin",
                OAuthAccount.provider_user_id == user_data["id"],
            )
            .first()
        )

        if oauth_account:
            logger.info(
                "Updating existing LinkedIn OAuth account for user: %s",
                oauth_account.user_id,
            )
            oauth_account.access_token = tokens["access_token"]
            oauth_account.profile_data = user_data
            oauth_account.updated_at = datetime.now(timezone.utc)
            user = oauth_account.user
        else:
            user = db.query(User).filter(User.email == user_data["email"]).first()

            if not user:
                logger.info(
                    "Creating new user account for LinkedIn user: %s",
                    user_data.get("email"),
                )
                user_service = UserService(db)

                base_username = user_data["email"].split("@")[0]
                base_username = "".join(
                    c if c.isalnum() or c in "_-" else "_" for c in base_username
                )
                if base_username and not base_username[0].isalnum():
                    base_username = "user_" + base_username
                if not base_username:
                    base_username = "linkedin_user"

                username = base_username
                counter = 1
                while user_service.is_username_taken(username):
                    username = f"{base_username}{counter}"
                    counter += 1

                user_create = UserCreate(
                    email=user_data["email"],
                    username=username,
                    first_name=user_data.get("given_name", ""),
                    last_name=user_data.get("family_name", ""),
                    password="oauth_user_no_password",
                )
                user = user_service.create_user(user_create)
                logger.info("Created new LinkedIn user with ID: %s", user.id)
            else:
                logger.info(
                    "Linking LinkedIn OAuth account to existing user: %s", user.id
                )

            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="linkedin",
                provider_user_id=user_data["id"],
                email=user_data["email"],
                access_token=tokens["access_token"],
                profile_data=user_data,
                created_at=datetime.now(timezone.utc),
            )
            db.add(oauth_account)

        db.commit()
        logger.info("LinkedIn OAuth account setup completed for user: %s", user.id)

        access_token = create_access_token(subject=user.id)
        logger.info("JWT token created for LinkedIn user: %s", user.id)

        newly_created_user = (
            not oauth_account
            or oauth_account.created_at
            >= datetime.now(timezone.utc) - timedelta(minutes=5)
        )

        if newly_created_user:
            callback_url = (
                f"{settings.FRONTEND_URL}/callback?token={access_token}&new_user=true"
            )
        else:
            callback_url = f"{settings.FRONTEND_URL}/callback?token={access_token}"

        logger.info("Redirecting to frontend callback: %s", callback_url.split("?")[0])
        return RedirectResponse(url=callback_url)

    except httpx.RequestError as e:
        logger.exception(
            "HTTP request failed during LinkedIn OAuth callback: %s", str(e)
        )
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=oauth_failed"
        return RedirectResponse(url=error_url)
    except Exception as e:
        logger.exception("LinkedIn OAuth callback failed: %s", str(e))
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=oauth_failed"
        return RedirectResponse(url=error_url)


@router.get("/tiktok/url")
def get_tiktok_oauth_url(db: Session = Depends(get_db)):
    """Get TikTok OAuth URL"""
    try:
        state = secrets.token_urlsafe(32)
        logger.info("Generating TikTok OAuth state %s", state[:8])

        logger.info("TIKTOK_CLIENT_ID set? %s", bool(settings.TIKTOK_CLIENT_ID))
        logger.info("TIKTOK_REDIRECT_URI: %s", settings.TIKTOK_REDIRECT_URI)

        oauth_state = OAuthState(
            state=state,
            provider="tiktok",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        db.add(oauth_state)
        db.commit()
        db.refresh(oauth_state)
        logger.info("OAuthState committed for provider=tiktok")

        params = {
            "client_key": settings.TIKTOK_CLIENT_ID,
            "redirect_uri": settings.TIKTOK_REDIRECT_URI,
            "response_type": "code",
            "scope": "user.info.basic",
            "state": state,
        }
        auth_url = "https://www.tiktok.com/v2/auth/authorize?" + urllib.parse.urlencode(
            params
        )
        return {"url": auth_url, "state": state}

    except Exception as e:
        logger.exception("Failed to build TikTok OAuth URL")
        raise HTTPException(
            status_code=500, detail=f"/tiktok/url failed: {type(e).__name__}: {e}"
        )


@router.get("/tiktok/callback")
def tiktok_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle TikTok OAuth callback"""
    try:
        logger.info(
            "TikTok OAuth callback received - code: %s, state: %s",
            code[:10] + "..." if code else "None",
            state[:8] + "..." if state else "None",
        )

        oauth_state = (
            db.query(OAuthState)
            .filter(
                OAuthState.state == state,
                OAuthState.provider == "tiktok",
                OAuthState.used.is_not(True),
                OAuthState.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

        if not oauth_state:
            logger.error("TikTok state verification failed for: %s", state[:8])
            error_url = f"{settings.FRONTEND_URL}/auth/error?message=invalid_state"
            return RedirectResponse(url=error_url)

        oauth_state.used = True
        db.commit()
        logger.info("TikTok OAuth state marked as used: %s", state[:8])

        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        token_data = {
            "client_key": settings.TIKTOK_CLIENT_ID,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        }

        logger.info("Exchanging TikTok authorization code for access token")

        with httpx.Client() as client:
            token_response = client.post(
                token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
            logger.info("TikTok token response status: %d", token_response.status_code)
            if token_response.status_code != 200:
                logger.error("TikTok token response error: %s", token_response.text)
                token_response.raise_for_status()
            tokens = token_response.json()

        logger.info("Successfully received tokens from TikTok")

        profile_url = "https://open.tiktokapis.com/v2/user/info/"
        headers = {
            "Authorization": f"Bearer {tokens['access_token']}",
            "Content-Type": "application/json",
        }

        request_body = {"fields": ["open_id", "union_id", "avatar_url", "display_name"]}

        with httpx.Client() as client:
            profile_response = client.post(
                profile_url, headers=headers, json=request_body, timeout=10.0
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()

        user_info = profile_data["data"]["user"]

        user_data = {
            "id": user_info["open_id"],
            "email": None,
            "given_name": user_info.get("display_name", ""),
            "family_name": "",
            "name": user_info.get("display_name", "TikTok User"),
            "avatar_url": user_info.get("avatar_url", ""),
        }

        logger.info(
            "TikTok user data received for: %s", user_data.get("name", "unknown")
        )

        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == "tiktok",
                OAuthAccount.provider_user_id == user_data["id"],
            )
            .first()
        )

        if oauth_account:
            logger.info(
                "Updating existing TikTok OAuth account for user: %s",
                oauth_account.user_id,
            )
            oauth_account.access_token = tokens["access_token"]
            oauth_account.profile_data = user_data
            oauth_account.updated_at = datetime.now(timezone.utc)
            user = oauth_account.user
        else:
            generated_email = f"tiktok_{user_data['id']}@magicscholar.com"

            existing_user = db.query(User).filter(User.email == generated_email).first()

            if not existing_user:
                logger.info(
                    "Creating new user account for TikTok user: %s",
                    user_data.get("name"),
                )
                user_service = UserService(db)

                base_username = user_data.get("name", "tiktok_user").lower()
                base_username = "".join(
                    c if c.isalnum() or c in "_-" else "_" for c in base_username
                )
                if not base_username or not base_username[0].isalnum():
                    base_username = "tiktok_user"

                username = base_username
                counter = 1
                while user_service.is_username_taken(username):
                    username = f"{base_username}{counter}"
                    counter += 1

                user_create = UserCreate(
                    email=generated_email,
                    username=username,
                    first_name=user_data.get("given_name", ""),
                    last_name=user_data.get("family_name", ""),
                    password="oauth_user_no_password",
                )
                user = user_service.create_user(user_create)
                logger.info("Created new TikTok user with ID: %s", user.id)
            else:
                user = existing_user
                logger.info("Using existing user for TikTok OAuth: %s", user.id)

            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="tiktok",
                provider_user_id=user_data["id"],
                email=generated_email,
                access_token=tokens["access_token"],
                profile_data=user_data,
                created_at=datetime.now(timezone.utc),
            )
            db.add(oauth_account)

        db.commit()
        logger.info("TikTok OAuth account setup completed for user: %s", user.id)

        access_token = create_access_token(subject=user.id)
        logger.info("JWT token created for TikTok user: %s", user.id)

        newly_created_user = (
            not oauth_account
            or oauth_account.created_at
            >= datetime.now(timezone.utc) - timedelta(minutes=5)
        )

        if newly_created_user:
            callback_url = (
                f"{settings.FRONTEND_URL}/callback?token={access_token}&new_user=true"
            )
        else:
            callback_url = f"{settings.FRONTEND_URL}/callback?token={access_token}"

        logger.info("Redirecting to frontend callback: %s", callback_url.split("?")[0])
        return RedirectResponse(url=callback_url)

    except httpx.RequestError as e:
        logger.exception("HTTP request failed during TikTok OAuth callback: %s", str(e))
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=oauth_failed"
        return RedirectResponse(url=error_url)
    except Exception as e:
        logger.exception("TikTok OAuth callback failed: %s", str(e))
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=oauth_failed"
        return RedirectResponse(url=error_url)


@router.delete("/cleanup-expired-states")
async def cleanup_expired_states(db: Session = Depends(get_db)):
    expired_states = (
        db.query(OAuthState)
        .filter(OAuthState.expires_at < datetime.now(timezone.utc))
        .delete()
    )
    db.commit()
    return {"deleted": expired_states}
