import time
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from modules.profile.profile_router import router as profile_router
from modules.agent.agent_router import router as agent_router
from core.pg_listener import listen_to_task_updates
from core.custom_logging import logger

def create_application() -> FastAPI:
    application = FastAPI(
        title="Vanguard AI API",
        version="1.1.0",
        description="Core API with WebSocket & Dorking capabilities",
    )

    application.include_router(profile_router)
    application.include_router(agent_router)
    
    # Mount UI as static
    application.mount("/", StaticFiles(directory="UI", html=True), name="ui")

    @application.on_event("startup")
    async def startup_event():
        asyncio.create_task(listen_to_task_updates())
        logger.info("pg_listener_started")

    return application


app = create_application()

RATE_LIMIT_STORE: dict = {}
RATE_LIMIT_THRESHOLD = 10
WINDOW_SECONDS = 60


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/agent/scrape":
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[client_ip] = []

        RATE_LIMIT_STORE[client_ip] = [
            t for t in RATE_LIMIT_STORE[client_ip] if current_time - t < WINDOW_SECONDS
        ]

        if len(RATE_LIMIT_STORE[client_ip]) >= RATE_LIMIT_THRESHOLD:
            logger.warning(
                "rate_limit_exceeded", client_ip=client_ip, path=request.url.path
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )

        RATE_LIMIT_STORE[client_ip].append(current_time)

    return await call_next(request)


@app.post("/test/reset-rate-limit")
async def reset_rate_limit():
    RATE_LIMIT_STORE.clear()
    return {"status": "reset"}


@app.get("/health")
async def health_check():
    return {"status": "operational", "engine": "SqlAlchemy", "timestamp": time.time()}
