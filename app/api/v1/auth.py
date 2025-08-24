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


@router.get("/login/{provider}", tags=["OAuth"])
async def oauth_login(
    provider: str,
    db: Session = Depends(get_db),
    redirect_uri: Optional[str] = Query(None),
):
    """
    Initiates the OAuth login process by redirecting to the provider's authorization URL.
    """
    if provider not in settings.OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

    client_id = settings.OAUTH_PROVIDERS[provider]["client_id"]
    auth_url = settings.OAUTH_PROVIDERS[provider]["auth_url"]
    scope = settings.OAUTH_PROVIDERS[provider]["scope"]
    redirect_url = settings.OAUTH_PROVIDERS[provider]["redirect_uri"]

    state_token = secrets.token_urlsafe(16)
    state = OAuthState(
        provider=provider,
        state_token=state_token,
        redirect_uri=redirect_uri,
        created_at=datetime.utcnow(),
    )
    db.add(state)
    db.commit()

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_url,
        "scope": scope,
        "state": state_token,
    }
    url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)
