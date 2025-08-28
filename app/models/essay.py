# app/models/essay.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class EssayType(str, Enum):
    """Types of essays students can write"""

    PERSONAL_STATEMENT = "personal_statement"
    SUPPLEMENTAL = "supplemental"
    SCHOLARSHIP_SPECIFIC = "scholarship_specific"
    LEADERSHIP = "leadership"
    CHALLENGES_OVERCOME = "challenges_overcome"
    WHY_MAJOR = "why_major"
    WHY_SCHOOL = "why_school"
    COMMUNITY_SERVICE = "community_service"
    DIVERSITY = "diversity"
    CUSTOM = "custom"


class EssayStatus(str, Enum):
    """Essay completion and review status"""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    AI_REVIEW_REQUESTED = "ai_review_requested"
    AI_REVIEWED = "ai_reviewed"
    PEER_REVIEW = "peer_review"
    MENTOR_REVIEW = "mentor_review"
    FINAL = "final"
    SUBMITTED = "submitted"


class Essay(Base):
    """
    Essay model for storing student essays with AI assistance capabilities
    """

    __tablename__ = "essays"

    # Primary key and relationships
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Essay metadata
    title = Column(String(255), nullable=False)
    essay_type = Column(SQLEnum(EssayType), nullable=False, index=True)
    prompt = Column(Text, nullable=True)  # The essay prompt/question
    word_limit = Column(Integer, nullable=True)  # Word count limit

    # Essay content
    content = Column(Text, nullable=True)  # The actual essay text
    word_count = Column(Integer, default=0)

    # Status and workflow
    status = Column(SQLEnum(EssayStatus), default=EssayStatus.DRAFT, nullable=False)
    is_primary = Column(Boolean, default=False)  # Primary personal statement

    # AI assistance tracking
    ai_feedback_count = Column(Integer, default=0)
    last_ai_review_at = Column(DateTime(timezone=True), nullable=True)
    ai_suggestions = Column(JSON, nullable=True)  # Store AI suggestions
    ai_score = Column(Integer, nullable=True)  # AI-generated score 0-100

    # Version control for essay iterations
    version = Column(Integer, default=1)
    parent_essay_id = Column(Integer, ForeignKey("essays.id"), nullable=True)

    # Application-specific data
    target_schools = Column(JSON, nullable=True)  # Schools this essay is for
    target_scholarships = Column(JSON, nullable=True)  # Scholarships this essay is for

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="essays")
    essay_versions = relationship("Essay", remote_side=[id], backref="parent_essay")
    ai_interactions = relationship(
        "EssayAIInteraction", back_populates="essay", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Essay(id={self.id}, user_id={self.user_id}, type={self.essay_type}, status={self.status})>"

    @property
    def is_over_limit(self) -> bool:
        """Check if essay exceeds word limit"""
        if self.word_limit and self.word_count:
            return self.word_count > self.word_limit
        return False

    @property
    def completion_percentage(self) -> int:
        """Calculate essay completion percentage"""
        if not self.content:
            return 0

        if not self.word_limit:
            return 100 if len(self.content.strip()) > 50 else 50

        progress = min((self.word_count / self.word_limit) * 100, 100)
        return int(progress)


class EssayAIInteraction(Base):
    """
    Track AI interactions with essays for analytics and improvement
    """

    __tablename__ = "essay_ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    essay_id = Column(Integer, ForeignKey("essays.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Interaction details
    interaction_type = Column(
        String(50), nullable=False
    )  # "grammar_check", "style_review", "structure_analysis", etc.
    ai_model = Column(String(50), nullable=True)  # "gpt-4", "claude-3", etc.

    # Input/Output
    user_request = Column(Text, nullable=True)  # What the user asked for
    ai_response = Column(JSON, nullable=True)  # AI's structured response

    # Metrics
    processing_time_ms = Column(Integer, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 star rating from user
    was_helpful = Column(Boolean, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    essay = relationship("Essay", back_populates="ai_interactions")
    user = relationship("User")


class EssayTemplate(Base):
    """
    Essay templates and prompts for different schools/scholarships
    """

    __tablename__ = "essay_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template metadata
    name = Column(String(255), nullable=False)
    essay_type = Column(SQLEnum(EssayType), nullable=False)
    prompt_text = Column(Text, nullable=False)

    # Constraints
    word_limit = Column(Integer, nullable=True)
    character_limit = Column(Integer, nullable=True)

    # Source information
    school_name = Column(String(255), nullable=True)
    scholarship_name = Column(String(255), nullable=True)
    application_year = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
