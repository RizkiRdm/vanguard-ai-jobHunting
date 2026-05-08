import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.database import Base
import os

from dotenv import load_dotenv
load_dotenv()

# Standard DSN
DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost:5432/vanguard"))

# SQLAlchemy specific URL
SQLA_DATABASE_URL = DATABASE_URL
if SQLA_DATABASE_URL and SQLA_DATABASE_URL.startswith("postgresql://"):
    SQLA_DATABASE_URL = SQLA_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif SQLA_DATABASE_URL and SQLA_DATABASE_URL.startswith("postgres://"):
    SQLA_DATABASE_URL = SQLA_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(SQLA_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
