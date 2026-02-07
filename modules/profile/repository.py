from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
from modules.profile.models import UserProfile, UserExperience, UserSkill


class ProfileRepository:
    """
    Handles all database operations for User Profiles, Experiences, and Skills.
    Designed for AsyncSession to maintain high performance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --- PROFILE HEADER OPERATIONS ---

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """
        Fetches the full profile including nested relationships (Experiences & Skills).
        Uses selectinload for efficient Eager Loading.
        """
        result = await self.db.execute(
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                selectinload(UserProfile.experiences), selectinload(UserProfile.skills)
            )
        )
        return result.scalars().first()

    async def create_or_update_profile(self, user_id: UUID, **data) -> UserProfile:
        """
        Creates a profile if it doesn't exist, or updates an existing one.
        """
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id, **data)
            self.db.add(profile)
        else:
            for key, value in data.items():
                setattr(profile, key, value)

        await self.db.flush()
        return profile

    # --- EXPERIENCE OPERATIONS ---

    async def add_experience(self, profile_id: UUID, **data) -> UserExperience:
        """Adds a new work experience entry to a profile."""
        exp = UserExperience(profile_id=profile_id, **data)
        self.db.add(exp)
        await self.db.flush()
        return exp

    async def delete_experience(self, experience_id: UUID):
        """Removes a specific work experience entry."""
        await self.db.execute(
            delete(UserExperience).where(UserExperience.id == experience_id)
        )
        await self.db.flush()

    # --- SKILL OPERATIONS ---

    async def sync_skills(self, profile_id: UUID, skill_list: List[dict]):
        """
        Syncs the skills by removing old ones and inserting new ones.
        Simplest way to handle list updates in a 3NF structure.
        """
        # Remove existing skills first
        await self.db.execute(
            delete(UserSkill).where(UserSkill.profile_id == profile_id)
        )

        # Add new ones
        new_skills = [UserSkill(profile_id=profile_id, **s) for s in skill_list]
        self.db.add_all(new_skills)
        await self.db.flush()
        return new_skills

    async def commit(self):
        """Finalizes the transaction."""
        await self.db.commit()
