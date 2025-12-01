# app/models/__init__.py
"""
UPDATED: Added scholarship application tracking
"""

from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.models.scholarship import Scholarship

from app.models.oauth import OAuthAccount, OAuthState

# Admissions/Enrollment/Graduation


# NEW: Scholarship tracking
from app.models.scholarship_applications import ScholarshipApplication

from app.models.college_applications import CollegeApplication

# CampusConnect images

from app.models.entity_image import EntityImage


__all__ = [
    "User",
    "UserProfile",
    "Institution",
    "Scholarship",
    "OAuthAccount",
    "OAuthState",
    "AdmissionsData",
    "EnrollmentData",
    "GraduationData",
    "ScholarshipApplication",
    "CollegeApplication",
    "EntityImage",
]
