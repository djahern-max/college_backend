# app/models/__init__.py
"""
UPDATED: Added scholarship application tracking
"""

from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.tuition import TuitionData
from app.models.oauth import OAuthAccount, OAuthState

# Admissions/Enrollment/Graduation
from app.models.admissions import AdmissionsData
from app.models.enrollment import EnrollmentData
from app.models.graduation import GraduationData

# NEW: Scholarship tracking
from app.models.scholarship_applications import ScholarshipApplication

from app.models.college_applications import CollegeApplication


__all__ = [
    "User",
    "UserProfile",
    "Institution",
    "Scholarship",
    "TuitionData",
    "OAuthAccount",
    "OAuthState",
    "AdmissionsData",
    "EnrollmentData",
    "GraduationData",
    # NEW
    "ScholarshipApplication",
    "CollegeApplication",
]
