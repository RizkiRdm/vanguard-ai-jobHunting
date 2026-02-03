import asyncio
import sys
from core.database import engine, Base

# Import all models here to ensure they are registered on Base.metadata
from core.models_tech import AgentTask, AgentExecutionLog, LLMUsageLog


async def init_models():
    """
    Drops all tables (optional, use with caution) and creates new ones
    based on the SQLAlchemy models defined in the core layer.
    """
    print("Connecting to the database to initialize models...")

    async with engine.begin() as conn:
        # Uncomment the line below if you want to clear the DB every time (NOT FOR PROD)
        # await conn.run_sync(Base.metadata.drop_all)

        print("Creating tables in progress...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully! Fr fr, no cap.")


if __name__ == "__main__":
    try:
        asyncio.run(init_models())
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)
