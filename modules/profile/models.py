from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from uuid import UUID, uuid4
from datetime import datetime
from core.database import Base
from core.security import mask_email

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), default="LOCAL")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    profile: Mapped["UserProfile"] = relationship(back_populates="user")

    @property
    def masked_email(self):
        return mask_email(self.email)

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    starter_cv_path: Mapped[str] = mapped_column(String(512), nullable=True)
    summary: Mapped[str] = mapped_column(nullable=True)
    target_role: Mapped[str] = mapped_column(String(255), nullable=True)
    expected_salary: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
