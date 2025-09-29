# app/models/__init__.py
from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.models.institution_match import InstitutionMatch  # ADD THIS
from app.models.scholarship import Scholarship, ScholarshipMatch
from app.models.tuition import TuitionData
from app.models.oauth import OAuthAccount, OAuthState
from app.models.essay import Essay

__all__ = [
    "User",
    "UserProfile",
    "Institution",
    "InstitutionMatch",  # ADD THIS
    "Scholarship",
    "ScholarshipMatch",
    "TuitionData",
    "OAuthAccount",
    "OAuthState",
    "Essay",
]
