import asyncio
import pytest
from tortoise import Tortoise
from core.database import TORTOISE_CONFIG
from modules.profile.models import User, UserProfile


@pytest.mark.asyncio
async def test_database_handshake():
    import copy

    # 1. Clone config asli agar tidak merusak config global
    test_config = copy.deepcopy(TORTOISE_CONFIG)

    # 2. Fix URL (seperti langkah sebelumnya)
    original_url = test_config["connections"]["default"]
    test_config["connections"]["default"] = original_url.replace(
        "postgresql+asyncpg://", "postgres://"
    ).replace("postgresql://", "postgres://")

    # 3. BUANG 'aerich' dari daftar apps jika ada
    # Ini untuk mencegah error: Module "aerich.models" not found
    if "models" in test_config["apps"]:
        # Hapus 'aerich.models' dari list jika ada di sana
        if "aerich.models" in test_config["apps"]["models"]["models"]:
            test_config["apps"]["models"]["models"].remove("aerich.models")

    # Jika aerich ada sebagai app terpisah (biasanya nama app-nya 'models')
    # pastikan modulnya valid atau hapus saja untuk keperluan handshake test

    try:
        await Tortoise.init(config=test_config)
        print("✅ SUCCESS: Tortoise initialized without aerich dependency.")

        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")

        # generate_schemas akan membuat semua tabel dari model yang terdaftar
        await Tortoise.generate_schemas()
        print("✅ SUCCESS: Database Handshake & Schema Sync completed.")

    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    # Script ini bisa dijalankan langsung dengan 'python tests/unit/test_db_connection.py'
    # atau via 'pytest tests/unit/test_db_connection.py'
    asyncio.run(test_database_handshake())
