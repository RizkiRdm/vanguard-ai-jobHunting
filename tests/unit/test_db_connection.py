import asyncio
import pytest
from tortoise import Tortoise
from core.database import TORTOISE_CONFIG
from modules.profile.models import User, UserProfile


@pytest.mark.asyncio
async def test_database_handshake():
    import copy

    # 1. Clone the original configuration to avoid damaging the global configuration.
    test_config = copy.deepcopy(TORTOISE_CONFIG)

    # 2. Fix the URL
    original_url = test_config["connections"]["default"]
    test_config["connections"]["default"] = original_url.replace(
        "postgresql+asyncpg://", "postgres://"
    ).replace("postgresql://", "postgres://")

    # 3. Remove ‘aerich’ from the list of apps if it is there.
    if "models" in test_config["apps"]:
        if "aerich.models" in test_config["apps"]["models"]["models"]:
            test_config["apps"]["models"]["models"].remove("aerich.models")
    try:
        await Tortoise.init(config=test_config)
        print("✅ SUCCESS: Tortoise initialized without aerich dependency.")

        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")

        # generate_schemas will create all tables from the registered models
        await Tortoise.generate_schemas()
        print("✅ SUCCESS: Database Handshake & Schema Sync completed.")

    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_database_handshake())
