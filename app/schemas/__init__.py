# app/schemas/__init__.py
"""
Pydantic schemas for CampusConnect API.

These schemas define the structure of data that flows between the frontend and backend:
- Request validation: Ensure incoming data is properly formatted
- Response formatting: Standardize API responses
- Documentation: Automatic OpenAPI/Swagger documentation generation

Schema categories:
- auth: Authentication and authorization
- user: User management and profiles
- profile: User profile management
"""

from .auth import (
    Token,
    TokenData,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    OAuthLoginRequest,
    OAuthURL,
)

from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB

from .profile import (
    ProfileBase,
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileSummary,
    ProfileFieldUpdate,
    ProfileSection,
    ProfileCompletionStatus,
)

# Export all schemas
__all__ = [
    # Auth schemas
    "Token",
    "TokenData",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "OAuthLoginRequest",
    "OAuthURL",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Profile schemas
    "ProfileBase",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ProfileSummary",
    "ProfileFieldUpdate",
    "ProfileSection",
    "ProfileCompletionStatus",
]
