# app/models/institution.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Enum as SQLEnum,
    Text,
    Index,
    desc,
    and_,
    or_,
    func,
)
from sqlalchemy.orm import Session, relationship
from app.core.database import Base
from enum import Enum
from datetime import datetime
from typing import Optional, List


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


class ImageExtractionStatus(str, Enum):
    """Status of image extraction process"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    FALLBACK_APPLIED = "fallback_applied"


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

    # ===========================
    # IMAGE INFORMATION
    # ===========================
    primary_image_url = Column(
        String(500),
        nullable=True,
        comment="CDN URL to standardized 400x300px image for school cards",
    )
    primary_image_quality_score = Column(
        Integer,
        nullable=True,
        comment="Quality score 0-100 for ranking schools by image quality",
        index=True,
    )

    customer_rank = Column(
        Integer,
        nullable=True,
        comment="Customer ranking for advertising priority (higher = better placement)",
        index=True,
    )

    logo_image_url = Column(
        String(500),
        nullable=True,
        comment="CDN URL to school logo for headers/search results",
    )
    image_extraction_status = Column(
        SQLEnum(ImageExtractionStatus),
        default=ImageExtractionStatus.PENDING,
        index=True,
        comment="Status of image extraction process",
    )
    image_extraction_date = Column(
        DateTime, nullable=True, comment="When images were last extracted/updated"
    )

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

    step2_financial_data = relationship(
        "Step2_IC2023_AY", back_populates="institution", uselist=False
    )

    def __repr__(self):
        return f"<Institution(id={self.id}, name='{self.name}', state='{self.state}')>"

    # ===========================
    # COMPUTED PROPERTIES
    # ===========================
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

    @property
    def has_high_quality_image(self) -> bool:
        """Check if institution has a high-quality image (score 80+)"""
        return (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score >= 80
        )

    @property
    def has_good_image(self) -> bool:
        """Check if institution has a good quality image (score 60+)"""
        return (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score >= 60
        )

    @property
    def image_needs_attention(self) -> bool:
        """Check if image needs manual review or improvement"""
        return self.image_extraction_status in [
            ImageExtractionStatus.FAILED,
            ImageExtractionStatus.NEEDS_REVIEW,
        ] or (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score < 40
        )

    @property
    def display_image_url(self) -> Optional[str]:
        """Return the best available image URL for display"""
        if self.primary_image_url:
            return self.primary_image_url
        elif self.logo_image_url:
            return self.logo_image_url
        else:
            # Return a placeholder or category-based fallback
            return self._get_fallback_image_url()

    def _get_fallback_image_url(self) -> str:
        """Get fallback image based on institution characteristics"""
        base_url = "https://magicscholar-images.nyc3.digitaloceanspaces.com/fallbacks/"

        # You can customize these based on your fallback image strategy
        if self.control_type == ControlType.PUBLIC:
            if self.size_category in [SizeCategory.LARGE, SizeCategory.VERY_LARGE]:
                return f"{base_url}large_public_university.jpg"
            else:
                return f"{base_url}public_college.jpg"
        elif self.control_type == ControlType.PRIVATE_NONPROFIT:
            return f"{base_url}private_college.jpg"
        else:
            return f"{base_url}general_institution.jpg"

    # ===========================
    # INSTANCE METHODS
    # ===========================
    def update_image_info(
        self,
        image_url: str,
        quality_score: int,
        logo_url: Optional[str] = None,
        status: ImageExtractionStatus = ImageExtractionStatus.SUCCESS,
    ):
        """Update image information for the institution"""
        self.primary_image_url = image_url
        self.primary_image_quality_score = quality_score
        if logo_url:
            self.logo_image_url = logo_url
        self.image_extraction_status = status
        self.image_extraction_date = datetime.utcnow()

    def update_customer_rank(self, new_rank: int) -> None:
        """Update customer ranking (for when they upgrade/downgrade their advertising package)"""
        self.customer_rank = new_rank

    # ===========================
    # CLASS METHODS FOR QUERIES
    # ===========================
    @classmethod
    def get_by_image_quality(
        cls, session: Session, limit: int = 50, min_score: int = 60
    ) -> List["Institution"]:
        """Get institutions ordered by image quality for featured display"""
        return (
            session.query(cls)
            .filter(cls.primary_image_quality_score >= min_score)
            .order_by(desc(cls.primary_image_quality_score))
            .limit(limit)
            .all()
        )

    @classmethod
    def get_needing_image_review(cls, session: Session) -> List["Institution"]:
        """Get institutions that need manual image review"""
        return (
            session.query(cls)
            .filter(
                or_(
                    cls.image_extraction_status == ImageExtractionStatus.NEEDS_REVIEW,
                    cls.image_extraction_status == ImageExtractionStatus.FAILED,
                    cls.primary_image_quality_score < 40,
                )
            )
            .order_by(desc(cls.primary_image_quality_score))
            .all()
        )

    @classmethod
    def get_featured_institutions(
        cls, db: Session, limit: int = 20, offset: int = 0, min_quality: int = 60
    ) -> List["Institution"]:
        """Get featured institutions ordered by customer_rank first, then image quality"""
        return (
            db.query(cls)
            .filter(
                and_(
                    cls.primary_image_url.isnot(None),
                    cls.primary_image_quality_score >= min_quality,
                )
            )
            .order_by(
                desc(cls.customer_rank.nullslast()),
                desc(cls.primary_image_quality_score.nullslast()),
                cls.name,
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    @classmethod
    def get_by_customer_priority(
        cls, db: Session, limit: int = 50, offset: int = 0
    ) -> List["Institution"]:
        """Get institutions ordered by customer ranking (advertising priority)"""
        return (
            db.query(cls)
            .order_by(
                desc(cls.customer_rank.nullslast()),
                desc(cls.primary_image_quality_score.nullslast()),
                cls.name,
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    # ===========================
    # TABLE CONSTRAINTS & INDEXES
    # ===========================
    __table_args__ = (
        Index("idx_institution_name", "name"),
        Index("idx_institution_state_city", "state", "city"),
        Index("idx_institution_control_size", "control_type", "size_category"),
        Index("idx_institution_image_quality", "primary_image_quality_score"),
        Index("idx_institution_customer_rank", "customer_rank"),
    )
