# app/models/institution.py - SIMPLIFIED VERSION
"""
Streamlined Institution model - removed 13 unused fields (59% reduction)
Only includes fields that are actually being used in production
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from typing import List, Optional


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"


class Institution(Base):
    """
    Simplified Institution model - only fields with actual data
    Removed 13 unused fields for better performance and maintainability
    """

    __tablename__ = "institutions"

    # ===========================
    # CORE IDENTIFICATION
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)

    # ===========================
    # LOCATION
    # ===========================
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)

    # ===========================
    # CLASSIFICATION
    # ===========================
    control_type = Column(SQLEnum(ControlType), nullable=False, index=True)

    # ===========================
    # DISPLAY & BRANDING
    # ===========================
    primary_image_url = Column(String(500), nullable=True)

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ===========================
    # RELATIONSHIPS
    # ===========================
    tuition_data = relationship(
        "TuitionData", back_populates="institution", cascade="all, delete-orphan"
    )

    # ===========================
    # COMPUTED PROPERTIES
    # ===========================
    @property
    def display_name(self) -> str:
        """Return name with location for display"""
        return f"{self.name} ({self.city}, {self.state})"

    @property
    def is_public(self) -> bool:
        """Check if institution is public"""
        return self.control_type == ControlType.PUBLIC

    @property
    def is_private(self) -> bool:
        """Check if institution is private"""
        return self.control_type in [
            ControlType.PRIVATE_NONPROFIT,
            ControlType.PRIVATE_FOR_PROFIT,
        ]

    # ===========================
    # CLASS METHODS FOR QUERIES
    # ===========================
    @classmethod
    def get_by_state(
        cls, db: Session, state: str, limit: int = 50
    ) -> List["Institution"]:
        """Get institutions by state"""
        return (
            db.query(cls)
            .filter(cls.state == state)
            .order_by(cls.name)
            .limit(limit)
            .all()
        )

    # ===========================
    # TABLE INDEXES
    # ===========================
    __table_args__ = (Index("idx_institution_state_city", "state", "city"),)

    def __repr__(self):
        return f"<Institution(id={self.id}, name='{self.name}', state='{self.state}')>"
