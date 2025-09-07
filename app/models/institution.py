# app/models/institution.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"


class SizeCategory(str, Enum):
    """Institution size categories"""

    VERY_SMALL = "very_small"  # <1,000
    SMALL = "small"  # 1,000-2,999
    MEDIUM = "medium"  # 3,000-9,999
    LARGE = "large"  # 10,000-19,999
    VERY_LARGE = "very_large"  # 20,000+


class USRegion(str, Enum):
    """US Regions for institutions"""

    NEW_ENGLAND = "new_england"
    MID_ATLANTIC = "mid_atlantic"
    EAST_NORTH_CENTRAL = "east_north_central"
    WEST_NORTH_CENTRAL = "west_north_central"
    SOUTH_ATLANTIC = "south_atlantic"
    EAST_SOUTH_CENTRAL = "east_south_central"
    WEST_SOUTH_CENTRAL = "west_south_central"
    MOUNTAIN = "mountain"
    PACIFIC = "pacific"


class Institution(Base):
    """
    Institution/College model for MagicScholar
    Based on IPEDS data with essential fields for matching and display
    """

    __tablename__ = "institutions"

    # ===========================
    # PRIMARY KEY & IDENTIFICATION
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(
        Integer, unique=True, nullable=False, index=True
    )  # UNITID from IPEDS

    # ===========================
    # BASIC INFORMATION
    # ===========================
    name = Column(String(255), nullable=False, index=True)

    # ===========================
    # LOCATION INFORMATION
    # ===========================
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)  # Two-letter state code
    zip_code = Column(String(10), nullable=True)
    region = Column(SQLEnum(USRegion), nullable=True, index=True)

    # ===========================
    # CONTACT INFORMATION
    # ===========================
    website = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)

    # ===========================
    # LEADERSHIP
    # ===========================
    president_name = Column(String(255), nullable=True)
    president_title = Column(String(100), nullable=True)

    # ===========================
    # INSTITUTIONAL CHARACTERISTICS
    # ===========================
    control_type = Column(SQLEnum(ControlType), nullable=False, index=True)
    size_category = Column(SQLEnum(SizeCategory), nullable=True, index=True)

    def __repr__(self):
        return f"<Institution(id={self.id}, name='{self.name}', state='{self.state}')>"

    @property
    def full_address(self) -> str:
        """Return formatted full address"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        return ", ".join(parts)

    @property
    def display_name(self) -> str:
        """Return name with location for display purposes"""
        if self.city and self.state:
            return f"{self.name} ({self.city}, {self.state})"
        return self.name

    @property
    def is_public(self) -> bool:
        """Check if institution is public"""
        return self.control_type == ControlType.PUBLIC

    @property
    def is_private(self) -> bool:
        """Check if institution is private (nonprofit or for-profit)"""
        return self.control_type in [
            ControlType.PRIVATE_NONPROFIT,
            ControlType.PRIVATE_FOR_PROFIT,
        ]
