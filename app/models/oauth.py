from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class OAuthAccount(Base):
    """
    OAuth Account model - links users to their social media accounts.
    Stores tokens and profile data from OAuth providers.
    """
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # OAuth provider information
    provider = Column(String, nullable=False)  # 'google', 'linkedin', 'tiktok'
    provider_user_id = Column(String, nullable=False)  # ID from the OAuth provider
    email = Column(String, nullable=True)  # Email from provider (if available)
    
    # Token storage (should be encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Store additional profile info from the provider
    profile_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="oauth_accounts")
    
    def __repr__(self):
        return f"<OAuthAccount(provider={self.provider}, user_id={self.user_id})>"


class OAuthState(Base):
    """
    OAuth State model - stores temporary state tokens for OAuth security.
    Prevents CSRF attacks during OAuth flow.
    """
    __tablename__ = "oauth_states"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=False)
    redirect_url = Column(String, nullable=True)  # Where to redirect after OAuth
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f"<OAuthState(provider={self.provider}, state={self.state[:10]}...)>"
