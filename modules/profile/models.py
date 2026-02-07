from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, UTC
from core.database import Base


class UserProfile(Base):
    """
    Header for a user's CV/Resume data.
    """

    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )

    summary = Column(Text, nullable=True)
    target_role = Column(String(255), nullable=True)
    last_parsed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    # Relationships
    user = relationship("User", backref="profile", uselist=False)
    experiences = relationship(
        "UserExperience", back_populates="profile", cascade="all, delete-orphan"
    )
    skills = relationship(
        "UserSkill", back_populates="profile", cascade="all, delete-orphan"
    )


class UserExperience(Base):
    """
    Individual work experience entries (3NF).
    """

    __tablename__ = "user_experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    company_name = Column(String(150), nullable=False)
    role = Column(String(70), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # Null if still working there
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now(UTC))

    profile = relationship("UserProfile", back_populates="experiences")


class UserSkill(Base):
    """
    Individual skills associated with a profile (3NF).
    """

    __tablename__ = "user_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    skill_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # e.g., 'Technical', 'Soft Skill'

    created_at = Column(DateTime, default=datetime.now(UTC))

    profile = relationship("UserProfile", back_populates="skills")
