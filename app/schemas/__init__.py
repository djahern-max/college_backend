# app/schemas/__init__.py
"""
Export all schemas for easy importing
ADD THIS FILE if you don't have one already
"""

# Existing schemas (you may have more - add them here)
from app.schemas.institution import (
    InstitutionBase,
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionResponse,
    InstitutionDetailResponse,
    InstitutionList,
    InstitutionSearchFilter,
    InstitutionStats,
    ControlType,
)

# NEW: Export nested summary schemas too
from app.schemas.institution import (
    AdmissionsSummary,
    EnrollmentSummary,
    GraduationSummary,
)

# CampusConnect images
from app.schemas.entity_image import EntityImageResponse

__all__ = [
    # Institution schemas
    "InstitutionBase",
    "InstitutionCreate",
    "InstitutionUpdate",
    "InstitutionResponse",
    "InstitutionDetailResponse",
    "InstitutionList",
    "InstitutionSearchFilter",
    "InstitutionStats",
    "ControlType",
    # Summary schemas
    "AdmissionsSummary",
    "EnrollmentSummary",
    "GraduationSummary",
    # Entity image schema
    "EntityImageResponse",
]
