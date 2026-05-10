import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Standard DSN (e.g., for asyncpg or psql)
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy requires postgresql+asyncpg:// for async engines
SQLA_DATABASE_URL = DATABASE_URL
if SQLA_DATABASE_URL and SQLA_DATABASE_URL.startswith("postgresql://"):
    SQLA_DATABASE_URL = SQLA_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif SQLA_DATABASE_URL and SQLA_DATABASE_URL.startswith("postgres://"):
    SQLA_DATABASE_URL = SQLA_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(SQLA_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
