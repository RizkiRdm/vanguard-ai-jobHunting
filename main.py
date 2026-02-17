from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from core.database import TORTOISE_CONFIG

app = FastAPI(title="Vanguard AI API", version="0.1.0")


@app.get("/health")
async def health_check():
    return {"status": "operational", "engine": "Tortoise ORM"}


# Async Database Handshake integration
register_tortoise(
    app,
    config=TORTOISE_CONFIG,
    generate_schemas=True,  # Set False jika sudah menggunakan Aerich untuk migrasi prod
    add_exception_handlers=True,
)
