from sqlalchemy import String, Integer, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import UUID, uuid4
from datetime import datetime
from core.database import Base

class ScrapedJob(Base):
    __tablename__ = "scraped_jobs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    job_title: Mapped[str] = mapped_column(String(200))
    company_name: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    job_description: Mapped[str] = mapped_column(Text)
    similarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class TailoredDocument(Base):
    __tablename__ = "tailored_documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    task_id: Mapped[UUID] = mapped_column(index=True)
    doc_type: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    token_cost: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
