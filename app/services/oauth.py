# app/services/oauth.py - Simplified (Google + LinkedIn only)
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict, Any
import secrets

from app.core.config import settings
from app.models.user import User
from app.models.oauth import OAuthAccount


class OAuthService:
    """OAuth service for Google and LinkedIn authentication"""

    # =========================================================================
    # GOOGLE OAUTH
    # =========================================================================

    async def handle_google_callback(
        self, code: str, db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle Google OAuth callback and return user data"""

        # Exchange authorization code for access token
        token_data = await self._exchange_google_code(code)

        # Get user information from Google
        user_info = await self._get_google_user_info(token_data["access_token"])

        # Find or create user account
        user = await self._find_or_create_oauth_user(
            provider="google",
            provider_user_id=user_info["id"],
            email=user_info["email"],
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name"),
            profile_data=user_info,
            token_data=token_data,
            db=db,
        )

        return {"user": user, "provider": "google"}

    async def _exchange_google_code(self, code: str) -> Dict[str, Any]:
        """Exchange Google authorization code for access token"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()

    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # LINKEDIN OAUTH
    # =========================================================================

    async def handle_linkedin_callback(
        self, code: str, db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle LinkedIn OAuth callback and return user data"""

        # Exchange authorization code for access token
        token_data = await self._exchange_linkedin_code(code)

        # Get user profile from LinkedIn
        profile_info = await self._get_linkedin_user_info(token_data["access_token"])

        # Get user email from LinkedIn (separate API call)
        email_info = await self._get_linkedin_email(token_data["access_token"])

        # Combine profile and email information
        user_info = {
            **profile_info,
            "email": email_info["elements"][0]["handle~"]["emailAddress"],
        }

        # Find or create user account
        user = await self._find_or_create_oauth_user(
            provider="linkedin",
            provider_user_id=user_info["id"],
            email=user_info["email"],
            first_name=user_info.get("firstName", {}).get("localized", {}).get("en_US"),
            last_name=user_info.get("lastName", {}).get("localized", {}).get("en_US"),
            profile_data=user_info,
            token_data=token_data,
            db=db,
        )

        return {"user": user, "provider": "linkedin"}

    async def _exchange_linkedin_code(self, code: str) -> Dict[str, Any]:
        """Exchange LinkedIn authorization code for access token"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "client_id": settings.LINKEDIN_CLIENT_ID,
                    "client_secret": settings.LINKEDIN_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()

    async def _get_linkedin_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information from LinkedIn"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.linkedin.com/v2/people/~",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    async def _get_linkedin_email(self, access_token: str) -> Dict[str, Any]:
        """Get user email from LinkedIn"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.linkedin.com/v2/emailAddresses?q=members&projection=(elements*(handle~))",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # SHARED HELPER METHODS
    # =========================================================================

    async def _find_or_create_oauth_user(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        first_name: str,
        last_name: str,
        profile_data: Dict[str, Any],
        token_data: Dict[str, Any],
        db: AsyncSession,
    ) -> User:
        """Find existing user or create new one from OAuth data"""

        # First, try to find existing OAuth account
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
        )
        oauth_account = result.scalar_one_or_none()

        if oauth_account:
            # Update existing OAuth account with new token data
            oauth_account.access_token = token_data.get("access_token")
            oauth_account.refresh_token = token_data.get("refresh_token")
            oauth_account.profile_data = profile_data

            if "expires_in" in token_data:
                oauth_account.expires_at = datetime.utcnow() + timedelta(
                    seconds=token_data["expires_in"]
                )

            await db.commit()

            # Get the associated user
            result = await db.execute(
                select(User).where(User.id == oauth_account.user_id)
            )
            return result.scalar_one()

        # If email is provided, try to find existing user by email
        user = None
        if email:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

        if not user:
            # Create new user
            # Generate username from email or provider data
            if email:
                base_username = email.split("@")[0]
            else:
                base_username = f"{provider}_user"

            # Ensure username is unique
            username = await self._generate_unique_username(base_username, db)

            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                hashed_password=None,  # OAuth users don't have passwords
                is_active=True,
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Create OAuth account link
        oauth_account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            profile_data=profile_data,
        )

        if "expires_in" in token_data:
            oauth_account.expires_at = datetime.utcnow() + timedelta(
                seconds=token_data["expires_in"]
            )

        db.add(oauth_account)
        await db.commit()

        return user

    async def _generate_unique_username(
        self, base_username: str, db: AsyncSession
    ) -> str:
        """Generate a unique username by appending numbers if needed"""

        username = base_username
        counter = 1

        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                return username

            username = f"{base_username}_{counter}"
            counter += 1

            # Safety check to prevent infinite loop
            if counter > 1000:
                username = f"{base_username}_{secrets.token_hex(4)}"
                break

        return username
