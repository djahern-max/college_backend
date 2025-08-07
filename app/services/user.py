"""
User business logic service - FIXED VERSION
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """User service with business logic."""

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""
        return pwd_context.verify(plain_password, hashed_password)

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Hash the password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user data with hashed password - FIXED approach
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['hashed_password'] = hashed_password
        
        # Use the repository directly with the dict, not UserCreate schema
        db_obj = User(**user_dict)
        self.repository.db.add(db_obj)
        await self.repository.db.flush()
        await self.repository.db.refresh(db_obj)
        return db_obj

    async def get(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.repository.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.repository.get_by_username(username)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users."""
        return await self.repository.get_multi(skip=skip, limit=limit)

    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        update_dict = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if 'password' in update_dict:
            update_dict['hashed_password'] = self._hash_password(update_dict.pop('password'))
        
        return await self.repository.update(id=user_id, obj_in=update_dict)

    async def delete(self, user_id: int) -> Optional[User]:
        """Delete user."""
        return await self.repository.delete(id=user_id)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
