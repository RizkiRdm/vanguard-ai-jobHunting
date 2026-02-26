import os
import pytest
from tortoise import Tortoise
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(autouse=True)
async def db_setup():
    db_url = os.getenv("DATABASE_URL")

    # Tambahkan parameter pool langsung ke DSN
    pool_params = "minsize=2&maxsize=20"
    if "?" in db_url:
        db_url = f"{db_url}&{pool_params}"
    else:
        db_url = f"{db_url}?{pool_params}"

    # Reset state Tortoise dengan benar (await coroutine)
    await Tortoise._reset_apps()

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["modules.agent.models", "modules.profile.models"]},
    )
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()
