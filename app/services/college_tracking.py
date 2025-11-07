# app/services/college_tracking.py
"""
Service for college application tracking business logic
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date

from app.models.college_applications import CollegeApplication
from app.models.institution import Institution
from app.schemas.college_tracking import ApplicationStatus, ApplicationType


class CollegeTrackingService:
    """Handle college application tracking operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Get complete dashboard data for a user

        Returns:
            Dictionary with summary, upcoming deadlines, overdue, and all applications
        """
        # Get all applications with institution data
        applications = (
            self.db.query(CollegeApplication)
            .filter(CollegeApplication.user_id == user_id)
            .join(Institution)
            .order_by(CollegeApplication.deadline.asc())
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

    def save_college(
        self,
        user_id: int,
        institution_id: int,
        status: ApplicationStatus = ApplicationStatus.RESEARCHING,
        application_type: Optional[ApplicationType] = None,
        deadline: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> CollegeApplication:
        """
        Save a college to user's tracking

        Args:
            user_id: User's ID
            institution_id: Institution to save
            status: Initial status (default: RESEARCHING)
            application_type: Type of application (ED, EA, RD, Rolling)
            deadline: Application deadline
            notes: Optional notes

        Returns:
            CollegeApplication object

        Raises:
            ValueError: If college already saved or institution doesn't exist
        """
        # Check if already saved
        existing = (
            self.db.query(CollegeApplication)
            .filter(
                CollegeApplication.user_id == user_id,
                CollegeApplication.institution_id == institution_id,
            )
            .first()
        )

        if existing:
            raise ValueError("College already in your tracking")

        # Verify institution exists
        institution = (
            self.db.query(Institution).filter(Institution.id == institution_id).first()
        )

        if not institution:
            raise ValueError("Institution not found")

        # Create application
        application = CollegeApplication(
            user_id=user_id,
            institution_id=institution_id,
            status=status,
            application_type=application_type,
            deadline=deadline,
            notes=notes,
        )

        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)

        return application

    def update_application(
        self, application_id: int, user_id: int, **updates
    ) -> CollegeApplication:
        """
        Update a college application

        Auto-sets timestamps based on status changes:
        - IN_PROGRESS → sets started_at
        - SUBMITTED → sets submitted_at
        - ACCEPTED/REJECTED/WAITLISTED → sets decided_at

        Args:
            application_id: Application ID
            user_id: User's ID (for security)
            **updates: Fields to update

        Returns:
            Updated CollegeApplication

        Raises:
            ValueError: If application not found or doesn't belong to user
        """
        application = (
            self.db.query(CollegeApplication)
            .filter(
                CollegeApplication.id == application_id,
                CollegeApplication.user_id == user_id,
            )
            .first()
        )

        if not application:
            raise ValueError("Application not found")

        # Handle status changes and auto-set timestamps
        if "status" in updates:
            new_status = updates["status"]

            # Set started_at when moving to IN_PROGRESS
            if (
                new_status == ApplicationStatus.IN_PROGRESS
                and not application.started_at
            ):
                application.started_at = datetime.utcnow()

            # Set submitted_at when moving to SUBMITTED
            if (
                new_status == ApplicationStatus.SUBMITTED
                and not application.submitted_at
            ):
                application.submitted_at = datetime.utcnow()

            # Set decided_at when receiving decision
            if (
                new_status
                in [
                    ApplicationStatus.ACCEPTED,
                    ApplicationStatus.REJECTED,
                    ApplicationStatus.WAITLISTED,
                ]
                and not application.decided_at
            ):
                application.decided_at = datetime.utcnow()

        # Update fields
        for key, value in updates.items():
            if hasattr(application, key):
                setattr(application, key, value)

        application.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(application)

        return application

    def delete_application(self, application_id: int, user_id: int) -> bool:
        """
        Delete a college application

        Args:
            application_id: Application ID
            user_id: User's ID (for security)

        Returns:
            True if deleted

        Raises:
            ValueError: If application not found
        """
        application = (
            self.db.query(CollegeApplication)
            .filter(
                CollegeApplication.id == application_id,
                CollegeApplication.user_id == user_id,
            )
            .first()
        )

        if not application:
            raise ValueError("Application not found")

        self.db.delete(application)
        self.db.commit()

        return True

    # ===========================
    # PRIVATE HELPER METHODS
    # ===========================

    def _calculate_summary(
        self, applications: List[CollegeApplication]
    ) -> Dict[str, int]:
        """Calculate dashboard summary statistics"""
        total = len(applications)

        submitted = sum(
            1 for app in applications if app.status == ApplicationStatus.SUBMITTED
        )

        in_progress = sum(
            1 for app in applications if app.status == ApplicationStatus.IN_PROGRESS
        )

        accepted = sum(
            1 for app in applications if app.status == ApplicationStatus.ACCEPTED
        )

        waitlisted = sum(
            1 for app in applications if app.status == ApplicationStatus.WAITLISTED
        )

        rejected = sum(
            1 for app in applications if app.status == ApplicationStatus.REJECTED
        )

        # Awaiting decision = submitted but no decision yet
        awaiting_decision = sum(
            1
            for app in applications
            if app.status == ApplicationStatus.SUBMITTED and not app.decided_at
        )

        return {
            "total_applications": total,
            "submitted": submitted,
            "in_progress": in_progress,
            "accepted": accepted,
            "waitlisted": waitlisted,
            "rejected": rejected,
            "awaiting_decision": awaiting_decision,
        }

    def _get_upcoming_deadlines(
        self, applications: List[CollegeApplication]
    ) -> List[CollegeApplication]:
        """Get applications with deadlines in the next 30 days"""
        today = date.today()
        thirty_days = today + timedelta(days=30)

        upcoming = [
            app
            for app in applications
            if app.deadline
            and today <= app.deadline <= thirty_days
            and app.status
            not in [
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.ACCEPTED,
                ApplicationStatus.REJECTED,
                ApplicationStatus.DECLINED,
                ApplicationStatus.ENROLLED,
            ]
        ]

        return sorted(upcoming, key=lambda x: x.deadline)

    def _get_overdue_applications(
        self, applications: List[CollegeApplication]
    ) -> List[CollegeApplication]:
        """Get applications with past deadlines that aren't submitted"""
        today = date.today()

        overdue = [
            app
            for app in applications
            if app.deadline
            and app.deadline < today
            and app.status
            not in [
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.ACCEPTED,
                ApplicationStatus.REJECTED,
                ApplicationStatus.DECLINED,
                ApplicationStatus.ENROLLED,
            ]
        ]

        return sorted(overdue, key=lambda x: x.deadline)
