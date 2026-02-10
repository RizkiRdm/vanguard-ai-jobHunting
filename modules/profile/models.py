from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Date, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, UTC
from core.database import Base

try:
    from modules.auth.model import User
except ImportError:
    pass


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

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="profile", uselist=False)

    experiences = relationship(
        "UserExperience", back_populates="profile", cascade="all, delete-orphan"
    )
    skills = relationship(
        "UserSkill", back_populates="profile", cascade="all, delete-orphan"
    )


class UserExperience(Base):
    __tablename__ = "user_experiences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )
    company_name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("UserProfile", back_populates="experiences")


class UserSkill(Base):
    __tablename__ = "user_skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )
    skill_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("UserProfile", back_populates="skills")
