from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from modules.auth.model import User
from core.security import verify_password
import logging

logger = logging.getLogger("AuthService")


class AuthService:
    """
    Business logic for authentication and user management.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Verify the user's email and password based on the database.
        """
        try:
            # search user bases on email
            result = await self.db.execute(select(User).where(User.email == email))
            user = result.scalars().first()

            if not user:
                logger.debug(f"User with email {email} not found.")
                return None

            # verify password
            if not verify_password(password, user.hashed_password):
                logger.debug(f"Invalid password for user {email}.")
                return None

            return user

        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Utility for session checking"""
        result = await self.db.get(User, user_id)
        return result
