import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base


class User(Base):
    """
    Standard User model for authentication and profile linking.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
