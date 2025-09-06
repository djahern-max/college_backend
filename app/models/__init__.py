# app/models/__init__.py
"""
SQLAlchemy models for MagicScholar.

Import all models here to ensure they are registered with SQLAlchemy
when the application starts.
"""

from .user import User
from .profile import UserProfile
from .oauth import OAuthAccount, OAuthState


# Import other models as they're created:
# from .scholarship import Scholarship, ScholarshipMatch
# from .review import Review

__all__ = [
    "User",
    "UserProfile",
    "OAuthAccount",
    "OAuthState",
    # Add other models as they're created
]
