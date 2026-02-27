import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from core.database import TORTOISE_CONFIG
from modules.profile.profile_router import router as profile_router
from modules.agent.agent_router import router as agent_router
from core.custom_logging import logger

# Global in-memory store for rate limiting
# Using list for timestamps to track requests within a sliding window
RATE_LIMIT_STORE = defaultdict(list)
RATE_LIMIT_THRESHOLD = 10
WINDOW_SECONDS = 60


def create_application() -> FastAPI:
    """
    Initializes the FastAPI application with global configurations.
    """
    application = FastAPI(
        title="Vanguard AI API",
        version="0.1.0",
        description="Core API for Vanguard Job Hunting Assistant",
    )

    # Database integration with Tortoise ORM
    register_tortoise(
        application,
        config=TORTOISE_CONFIG,
        generate_schemas=True,  # Set to False if using migrations (Aerich) in production
        add_exception_handlers=True,
    )

    # Register Routers
    application.include_router(profile_router)
    application.include_router(agent_router)

    return application


app = create_application()


@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify API and DB connectivity."""
    return {"status": "operational", "engine": "Tortoise ORM", "timestamp": time.time()}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting on specific sensitive endpoints.
    Current limit: 10 requests per minute for /agent/scrape.
    """
    if request.url.path == "/agent/scrape":
        client_ip = request.client.host
        current_time = time.time()

        # Clean up expired timestamps using list comprehension (efficient built-in)
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


@app.post("/test/reset-rate-limit", tags=["Testing"])
async def reset_limit():
    """Utility endpoint to clear rate limit store during automated testing."""
    RATE_LIMIT_STORE.clear()
    return {"status": "cleared", "message": "Rate limit store has been reset."}
