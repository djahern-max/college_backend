"""
Database models for CampusConnect.

This module contains all SQLAlchemy models that define our database structure:
- User: Authentication and basic user information
- UserProfile: Comprehensive student profiles for scholarship matching
- OAuthAccount: OAuth provider integration (Google, LinkedIn, TikTok)
- OAuthState: OAuth security state management
"""

from .user import User
from .profile import UserProfile
from .oauth import OAuthAccount, OAuthState

# Export all models for easy importing
__all__ = ["User", "UserProfile", "OAuthAccount", "OAuthState"]
