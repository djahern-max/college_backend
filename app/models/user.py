from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User model - represents registered users in our system.
    Supports both traditional email/password and OAuth authentication.
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic user information
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Authentication
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - connects to other tables
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
    
    @property
    def full_name(self):
        """Return user's full name or username if names not available"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
