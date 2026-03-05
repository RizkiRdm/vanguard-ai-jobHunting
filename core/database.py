import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": DATABASE_URL.split("/")[-1].split("?")[0],
                "host": DATABASE_URL.split("@")[-1].split(":")[0],
                "password": DATABASE_URL.split(":")[2].split("@")[0],
                "port": DATABASE_URL.split(":")[-1].split("/")[0],
                "user": DATABASE_URL.split("//")[-1].split(":")[0],
                "minsize": 5,
                "maxsize": 30,
            },
        }
    },
    "apps": {
        "models": {
            "models": [
                "modules.profile.models",
                "modules.agent.models",
                "modules.generator.models",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}
