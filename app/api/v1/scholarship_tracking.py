# app/api/v1/scholarship_tracking.py
"""
API endpoints for scholarship application tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.scholarship_tracking import ScholarshipTrackingService
from app.schemas.scholarship_tracking import (
    ApplicationStatus,
    ScholarshipApplicationCreate,
    ScholarshipApplicationUpdate,
    ScholarshipApplicationResponse,
    ScholarshipDashboardResponse,
)

router = APIRouter()


# ===========================
# DASHBOARD
# ===========================


@router.get("/dashboard", response_model=ScholarshipDashboardResponse)
async def get_scholarship_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's scholarship dashboard with summary stats and deadlines

    Returns:
    - Summary statistics (total apps, submitted, in progress, etc.)
    - Upcoming deadlines (next 30 days)
    - Overdue applications
    - All applications
    """
    service = ScholarshipTrackingService(db)
    dashboard_data = service.get_user_dashboard(current_user.id)

    return dashboard_data


# ===========================
# APPLICATION MANAGEMENT
# ===========================


@router.post(
    "/applications",
    response_model=ScholarshipApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_scholarship(
    data: ScholarshipApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save/bookmark a scholarship to user's dashboard

    Creates a new tracking record for the scholarship
    """
    service = ScholarshipTrackingService(db)

    try:
        application = service.save_scholarship(
            user_id=current_user.id,
            scholarship_id=data.scholarship_id,
            status=data.status,
            notes=data.notes,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/applications", response_model=List[ScholarshipApplicationResponse])
async def get_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    sort_by: str = Query("deadline", regex="^(deadline|amount|saved_at|status)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's scholarship applications with filtering and sorting

    Query Parameters:
    - status: Filter by application status
    - sort_by: Sort field (deadline, amount, saved_at, status)
    - sort_order: Sort direction (asc, desc)
    """
    service = ScholarshipTrackingService(db)

    applications = service.get_applications_filtered(
        user_id=current_user.id,
        status=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return applications


@router.get(
    "/applications/{application_id}", response_model=ScholarshipApplicationResponse
)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific scholarship application by ID"""
    from app.models.scholarship_applications import ScholarshipApplication

    application = (
        db.query(ScholarshipApplication)
        .filter(
            ScholarshipApplication.id == application_id,
            ScholarshipApplication.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    return application


@router.put(
    "/applications/{application_id}", response_model=ScholarshipApplicationResponse
)
async def update_scholarship_application(
    application_id: int,
    update_data: ScholarshipApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a scholarship application's status, notes, etc.

    Auto-sets timestamps based on status changes:
    - IN_PROGRESS → sets started_at
    - SUBMITTED → sets submitted_at
    - ACCEPTED/REJECTED → sets decision_date
    """
    service = ScholarshipTrackingService(db)

    try:
        # Convert Pydantic model to dict, excluding unset fields
        updates = update_data.model_dump(exclude_unset=True)

        application = service.update_application(
            application_id=application_id, user_id=current_user.id, updates=updates
        )

        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scholarship_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a scholarship from user's tracking
    """
    service = ScholarshipTrackingService(db)

    try:
        service.delete_application(application_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===========================
# QUICK ACTIONS
# ===========================


@router.post(
    "/applications/{application_id}/mark-submitted",
    response_model=ScholarshipApplicationResponse,
)
async def mark_as_submitted(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark scholarship as submitted

    Sets status to SUBMITTED and records submitted_at timestamp
    """
    service = ScholarshipTrackingService(db)

    try:
        application = service.update_application(
            application_id=application_id,
            user_id=current_user.id,
            updates={"status": ApplicationStatus.SUBMITTED},
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/applications/{application_id}/mark-accepted",
    response_model=ScholarshipApplicationResponse,
)
async def mark_as_accepted(
    application_id: int,
    award_amount: Optional[int] = Query(None, description="Amount awarded (optional)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark scholarship as accepted/won

    Sets status to ACCEPTED and records decision_date
    Optionally records the award amount received
    """
    service = ScholarshipTrackingService(db)

    try:
        updates = {"status": ApplicationStatus.ACCEPTED}
        if award_amount is not None:
            updates["award_amount"] = award_amount

        application = service.update_application(
            application_id=application_id, user_id=current_user.id, updates=updates
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/applications/{application_id}/mark-rejected",
    response_model=ScholarshipApplicationResponse,
)
async def mark_as_rejected(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark scholarship as rejected

    Sets status to REJECTED and records decision_date
    """
    service = ScholarshipTrackingService(db)

    try:
        application = service.update_application(
            application_id=application_id,
            user_id=current_user.id,
            updates={"status": ApplicationStatus.REJECTED},
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
