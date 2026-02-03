import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Database URL from environment
# Default to a local postgres if not provided (but .env is assumed to exist)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/vanguard"
)

# Create Async Engine
# Low-spec optimization: pool_size and max_overflow are kept modest
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True only for heavy debugging
    pool_size=5,
    max_overflow=10,
)

# Create Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Dependency Injection for FastAPI
async def get_db():
    """
    FastAPI dependency that provides an async session.
    Ensures the session is closed after the request is finished.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
