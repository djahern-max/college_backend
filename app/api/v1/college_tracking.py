# app/api/v1/college_tracking.py
"""
API endpoints for college application tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.college_tracking import CollegeTrackingService
from app.schemas.college_tracking import (
    ApplicationStatus,
    CollegeApplicationCreate,
    CollegeApplicationUpdate,
    CollegeApplicationResponse,
    CollegeDashboardResponse,
)

router = APIRouter()


# ===========================
# DASHBOARD
# ===========================


@router.get("/dashboard", response_model=CollegeDashboardResponse)
async def get_college_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's college application dashboard with summary stats and deadlines

    Returns:
    - Summary statistics (total apps, submitted, in progress, accepted, etc.)
    - Upcoming deadlines (next 30 days)
    - Overdue applications
    - All applications
    """
    service = CollegeTrackingService(db)
    dashboard_data = service.get_user_dashboard(current_user.id)

    return dashboard_data


# ===========================
# APPLICATION MANAGEMENT
# ===========================


@router.post(
    "/applications",
    response_model=CollegeApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_college(
    data: CollegeApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save/bookmark a college to user's dashboard

    Creates a new tracking record for the college application
    """
    service = CollegeTrackingService(db)

    try:
        application = service.save_college(
            user_id=current_user.id,
            institution_id=data.institution_id,
            status=data.status,
            application_type=data.application_type,
            deadline=data.deadline,
            notes=data.notes,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications", response_model=List[CollegeApplicationResponse])
async def get_applications(
    status: Optional[ApplicationStatus] = Query(None),
    sort_by: str = Query("deadline", pattern="^(deadline|saved_at|status)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's college applications with filtering and sorting

    Query Parameters:
    - status: Filter by application status
    - sort_by: Sort field (deadline, saved_at, status)
    - sort_order: Sort direction (asc, desc)
    """
    from app.models.college_applications import CollegeApplication
    from app.models.institution import Institution

    query = (
        db.query(CollegeApplication)
        .filter(CollegeApplication.user_id == current_user.id)
        .join(Institution)
    )

    # Filter by status if provided
    if status:
        query = query.filter(CollegeApplication.status == status)

    # Sort
    if sort_by == "deadline":
        sort_column = CollegeApplication.deadline
    elif sort_by == "saved_at":
        sort_column = CollegeApplication.saved_at
    else:  # status
        sort_column = CollegeApplication.status

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    applications = query.all()
    return applications


@router.get("/applications/{application_id}", response_model=CollegeApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific college application by ID"""
    from app.models.college_applications import CollegeApplication

    application = (
        db.query(CollegeApplication)
        .filter(
            CollegeApplication.id == application_id,
            CollegeApplication.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.put(
    "/applications/{application_id}",
    response_model=CollegeApplicationResponse,
)
async def update_college_application(
    application_id: int,
    data: CollegeApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a college application's status, notes, etc.

    Auto-sets timestamps based on status changes:
    - IN_PROGRESS → sets started_at
    - SUBMITTED → sets submitted_at
    - ACCEPTED/REJECTED/WAITLISTED → sets decided_at
    """
    service = CollegeTrackingService(db)

    try:
        # Convert Pydantic model to dict, excluding None values
        updates = data.model_dump(exclude_none=True)

        application = service.update_application(
            application_id=application_id, user_id=current_user.id, **updates
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_college_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a college from user's tracking"""
    service = CollegeTrackingService(db)

    try:
        service.delete_application(application_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===========================
# QUICK ACTIONS
# ===========================


@router.post(
    "/applications/{application_id}/mark-submitted",
    response_model=CollegeApplicationResponse,
)
async def mark_as_submitted(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark college application as submitted

    Sets status to SUBMITTED and records submitted_at timestamp
    """
    service = CollegeTrackingService(db)

    try:
        application = service.update_application(
            application_id=application_id,
            user_id=current_user.id,
            status=ApplicationStatus.SUBMITTED,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/applications/{application_id}/mark-accepted",
    response_model=CollegeApplicationResponse,
)
async def mark_as_accepted(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark college application as accepted

    Sets status to ACCEPTED and records decided_at timestamp
    """
    service = CollegeTrackingService(db)

    try:
        application = service.update_application(
            application_id=application_id,
            user_id=current_user.id,
            status=ApplicationStatus.ACCEPTED,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/applications/{application_id}/mark-rejected",
    response_model=CollegeApplicationResponse,
)
async def mark_as_rejected(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark college application as rejected

    Sets status to REJECTED and records decided_at timestamp
    """
    service = CollegeTrackingService(db)

    try:
        application = service.update_application(
            application_id=application_id,
            user_id=current_user.id,
            status=ApplicationStatus.REJECTED,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/applications/{application_id}/mark-waitlisted",
    response_model=CollegeApplicationResponse,
)
async def mark_as_waitlisted(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick action: Mark college application as waitlisted

    Sets status to WAITLISTED and records decided_at timestamp
    """
    service = CollegeTrackingService(db)

    try:
        application = service.update_application(
            application_id=application_id,
            user_id=current_user.id,
            status=ApplicationStatus.WAITLISTED,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
