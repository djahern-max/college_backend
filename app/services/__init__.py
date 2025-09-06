# app/services/__init__.py
"""
Service layer for CampusConnect application.

Services contain business logic and handle database operations.
They act as an abstraction layer between API endpoints and database models.
"""

from .user import UserService
from .profile import ProfileService
from .oauth import OAuthService
from .college import CollegeService

__all__ = [
    "UserService",
    "ProfileService",
    "OAuthService",
    "CollegeService",
]
