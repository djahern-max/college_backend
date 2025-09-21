from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)

        db_user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate(self, identifier: str, password: str) -> Optional[User]:
        """
        Authenticate user with email or username
        Args:
            identifier: Email address or username
            password: User's password
        Returns:
            User object if authentication successful, None otherwise
        """
        # Try to find user by email first
        db_user = self.db.query(User).filter(User.email == identifier).first()

        # If not found by email, try username
        if not db_user:
            db_user = self.db.query(User).filter(User.username == identifier).first()

        # If user not found at all
        if not db_user:
            return None

        # Verify password
        if not verify_password(password, db_user.hashed_password):
            return None

        return db_user

    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        db_user = self.get_by_id(user_id)
        if db_user:
            db_user.last_login_at = datetime.utcnow()
            self.db.commit()

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def is_username_taken(
        self, username: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """Check if username is already taken"""
        query = self.db.query(User).filter(User.username == username)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

    def is_email_taken(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if email is already taken"""
        query = self.db.query(User).filter(User.email == email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None
