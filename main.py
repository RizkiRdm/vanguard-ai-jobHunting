import time

from fastapi import FastAPI, Request, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from core.database import TORTOISE_CONFIG
from collections import defaultdict
from modules.profile.profile_router import router as profile_router
from modules.agent.agent_router import router as agent_router

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

# Global store
rate_limit_store = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    if request.url.path == "/agent/scrape":
        rate_limit_store[client_ip] = [
            t for t in rate_limit_store[client_ip] if current_time - t < 60
        ]

        if len(rate_limit_store[client_ip]) >= 10:
            # Ganti raise dengan response manual agar middleware tidak error saat testing
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429, content={"detail": "Rate limit exceeded"}
            )

        rate_limit_store[client_ip].append(current_time)

    return await call_next(request)


# Helper untuk testing: Endpoint untuk reset rate limit
@app.post("/test/reset-rate-limit")
async def reset_limit():
    rate_limit_store.clear()
    return {"status": "cleared"}


app.include_router(agent_router)


# register routers

app.include_router(profile_router)
app.include_router(agent_router)
