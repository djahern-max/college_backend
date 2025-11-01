# app/models/__init__.py
"""
UPDATED: Added new admissions, enrollment, and graduation models
"""

from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.tuition import TuitionData
from app.models.oauth import OAuthAccount, OAuthState

# NEW IMPORTS
from app.models.admissions import AdmissionsData
from app.models.enrollment import EnrollmentData
from app.models.graduation import GraduationData


__all__ = [
    "User",
    "UserProfile",
    "Institution",
    # "InstitutionMatch",  # Commented out - was in __all__ but not imported
    "Scholarship",
    "TuitionData",
    "OAuthAccount",
    "OAuthState",
    # "Essay",  # Commented out - was in __all__ but not imported
    # NEW MODELS
    "AdmissionsData",
    "EnrollmentData",
    "GraduationData",
]
