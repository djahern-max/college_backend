# app/services/scholarship_tracking.py
"""
Service for scholarship application tracking business logic
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.scholarship_applications import ScholarshipApplication
from app.models.scholarship import Scholarship
from app.schemas.scholarship_tracking import ApplicationStatus


class ScholarshipTrackingService:
    """Handle scholarship application tracking operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Get complete dashboard data for a user

        Returns:
            Dictionary with summary, upcoming deadlines, overdue, and all applications
        """
        # Get all applications with scholarship data
        applications = (
            self.db.query(ScholarshipApplication)
            .filter(ScholarshipApplication.user_id == user_id)
            .join(Scholarship)
            .order_by(Scholarship.deadline.asc())
            .all()
        )

        # Calculate summary statistics
        summary = self._calculate_summary(applications)

        # Get upcoming deadlines (next 30 days)
        upcoming_deadlines = self._get_upcoming_deadlines(applications)

        # Get overdue applications
        overdue = self._get_overdue_applications(applications)

        return {
            "summary": summary,
            "upcoming_deadlines": upcoming_deadlines,
            "overdue": overdue,
            "applications": applications,
        }

    def save_scholarship(
        self,
        user_id: int,
        scholarship_id: int,
        status: ApplicationStatus = ApplicationStatus.INTERESTED,
        notes: Optional[str] = None,
    ) -> ScholarshipApplication:
        """
        Save a scholarship to user's tracking

        Args:
            user_id: User's ID
            scholarship_id: Scholarship to save
            status: Initial status (default: INTERESTED)
            notes: Optional notes

        Returns:
            Created ScholarshipApplication

        Raises:
            ValueError: If scholarship already saved or doesn't exist
        """
        # Check if scholarship exists
        scholarship = (
            self.db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )

        if not scholarship:
            raise ValueError("Scholarship not found")

        # Check if already saved
        existing = (
            self.db.query(ScholarshipApplication)
            .filter(
                ScholarshipApplication.user_id == user_id,
                ScholarshipApplication.scholarship_id == scholarship_id,
            )
            .first()
        )

        if existing:
            raise ValueError("Scholarship already saved to your dashboard")

        # Create new application tracking record
        application = ScholarshipApplication(
            user_id=user_id,
            scholarship_id=scholarship_id,
            status=status,
            notes=notes,
            saved_at=datetime.utcnow(),
        )

        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)

        return application

    def update_application(
        self, application_id: int, user_id: int, updates: Dict[str, Any]
    ) -> ScholarshipApplication:
        """
        Update a scholarship application

        Args:
            application_id: Application ID
            user_id: User ID (for ownership check)
            updates: Dictionary of fields to update

        Returns:
            Updated ScholarshipApplication

        Raises:
            ValueError: If application not found
        """
        application = (
            self.db.query(ScholarshipApplication)
            .filter(
                ScholarshipApplication.id == application_id,
                ScholarshipApplication.user_id == user_id,
            )
            .first()
        )

        if not application:
            raise ValueError("Application not found")

        # Update fields
        for field, value in updates.items():
            if value is not None and hasattr(application, field):
                setattr(application, field, value)

        # Auto-set timestamps based on status changes
        if "status" in updates:
            new_status = updates["status"]

            if (
                new_status == ApplicationStatus.IN_PROGRESS
                and not application.started_at
            ):
                application.started_at = datetime.utcnow()

            elif (
                new_status == ApplicationStatus.SUBMITTED
                and not application.submitted_at
            ):
                application.submitted_at = datetime.utcnow()

            elif new_status in [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]:
                if not application.decision_date:
                    application.decision_date = datetime.utcnow()

        application.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(application)

        return application

    def delete_application(self, application_id: int, user_id: int) -> bool:
        """
        Remove a scholarship from tracking

        Args:
            application_id: Application ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted

        Raises:
            ValueError: If application not found
        """
        application = (
            self.db.query(ScholarshipApplication)
            .filter(
                ScholarshipApplication.id == application_id,
                ScholarshipApplication.user_id == user_id,
            )
            .first()
        )

        if not application:
            raise ValueError("Application not found")

        self.db.delete(application)
        self.db.commit()

        return True

    def get_applications_filtered(
        self,
        user_id: int,
        status: Optional[ApplicationStatus] = None,
        sort_by: str = "deadline",
        sort_order: str = "asc",
    ) -> List[ScholarshipApplication]:
        """
        Get user's applications with filtering and sorting

        Args:
            user_id: User ID
            status: Filter by status (optional)
            sort_by: Sort field (deadline, amount, saved_at, status)
            sort_order: Sort direction (asc, desc)

        Returns:
            List of ScholarshipApplications
        """
        query = (
            self.db.query(ScholarshipApplication)
            .filter(ScholarshipApplication.user_id == user_id)
            .join(Scholarship)
        )

        # Filter by status
        if status:
            query = query.filter(ScholarshipApplication.status == status)

        # Sort
        if sort_by == "deadline":
            order_col = Scholarship.deadline
        elif sort_by == "amount":
            order_col = Scholarship.amount_max
        elif sort_by == "saved_at":
            order_col = ScholarshipApplication.saved_at
        elif sort_by == "status":
            order_col = ScholarshipApplication.status
        else:
            order_col = Scholarship.deadline

        if sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())

        return query.all()

    # ===========================
    # PRIVATE HELPER METHODS
    # ===========================
    def _calculate_summary(
        self, applications: List[ScholarshipApplication]
    ) -> Dict[str, int]:
        """Calculate summary statistics - UPDATED to include all status counts"""
        total = len(applications)

        # Count each status type
        interested = len(
            [a for a in applications if a.status == ApplicationStatus.INTERESTED]
        )
        planning = len(
            [a for a in applications if a.status == ApplicationStatus.PLANNING]
        )
        in_progress = len(
            [a for a in applications if a.status == ApplicationStatus.IN_PROGRESS]
        )
        submitted = len(
            [a for a in applications if a.status == ApplicationStatus.SUBMITTED]
        )
        accepted = len(
            [a for a in applications if a.status == ApplicationStatus.ACCEPTED]
        )
        rejected = len(
            [a for a in applications if a.status == ApplicationStatus.REJECTED]
        )
        not_pursuing = len(
            [a for a in applications if a.status == ApplicationStatus.NOT_PURSUING]
        )

        # Calculate potential value (for active applications)
        active_statuses = [
            ApplicationStatus.INTERESTED,
            ApplicationStatus.PLANNING,
            ApplicationStatus.IN_PROGRESS,
            ApplicationStatus.SUBMITTED,
        ]

        total_potential = sum(
            app.scholarship.amount_max or 0
            for app in applications
            if app.status in active_statuses and app.scholarship.amount_max
        )

        # Calculate awarded value
        total_awarded = sum(
            app.award_amount or 0
            for app in applications
            if app.status == ApplicationStatus.ACCEPTED
        )

        # UPDATED: Return dictionary now includes all status counts
        return {
            "total_applications": total,
            "interested": interested,  # NEW
            "planning": planning,  # NEW
            "in_progress": in_progress,
            "submitted": submitted,
            "accepted": accepted,
            "rejected": rejected,  # NEW
            "not_pursuing": not_pursuing,  # NEW
            "total_potential_value": total_potential,
            "total_awarded_value": total_awarded,
        }

    def _get_upcoming_deadlines(
        self, applications: List[ScholarshipApplication]
    ) -> List[ScholarshipApplication]:
        """Get applications with deadlines in next 30 days"""
        today = datetime.utcnow()
        cutoff_date = (today + timedelta(days=30)).date()

        active_statuses = [
            ApplicationStatus.INTERESTED,
            ApplicationStatus.PLANNING,
            ApplicationStatus.IN_PROGRESS,
        ]

        upcoming = [
            app
            for app in applications
            if app.scholarship.deadline
            and app.scholarship.deadline >= today.date()
            and app.scholarship.deadline <= cutoff_date
            and app.status in active_statuses
        ]

        # Sort by deadline
        upcoming.sort(key=lambda x: x.scholarship.deadline)

        return upcoming[:5]  # Return top 5

    def _get_overdue_applications(
        self, applications: List[ScholarshipApplication]
    ) -> List[ScholarshipApplication]:
        """Get applications with past deadlines that aren't submitted"""
        today = datetime.utcnow()

        incomplete_statuses = [
            ApplicationStatus.INTERESTED,
            ApplicationStatus.PLANNING,
            ApplicationStatus.IN_PROGRESS,
        ]

        overdue = [
            app
            for app in applications
            if app.scholarship.deadline
            and app.scholarship.deadline < today.date()
            and app.status in incomplete_statuses
        ]

        return overdue
