import time
from collections import defaultdict
from typing import List, Dict

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from core.database import TORTOISE_CONFIG
from core.custom_logging import logger
from core.security import get_current_user_from_cookie
from modules.profile.profile_router import router as profile_router
from modules.agent.agent_router import router as agent_router

# Configuration: Heavy AI tasks are limited per USER, others per IP
LIMIT_CONFIG = {
    "/agent/apply": {"limit": 5, "window": 60, "auth_required": True},
    "/agent/scrape": {"limit": 5, "window": 60, "auth_required": True},
    "default": {"limit": 60, "window": 60, "auth_required": False},
}

rate_limit_store: Dict[str, Dict[str, List[float]]] = defaultdict(
    lambda: defaultdict(list)
)


def create_application() -> FastAPI:
    application = FastAPI(title="Vanguard AI API Gateway")

    register_tortoise(
        application,
        config=TORTOISE_CONFIG,
        generate_schemas=True,
        add_exception_handlers=True,
    )

    application.include_router(profile_router)
    application.include_router(agent_router)

    return application


app = create_application()


@app.middleware("http")
async def gateway_logic_middleware(request: Request, call_next):
    path = request.url.path
    current_time = time.time()

    # 1. Get config for current path
    config = LIMIT_CONFIG.get(path, LIMIT_CONFIG["default"])

    # 2. IDENTIFY IDENTIFIER (This is where get_current_user_from_cookie is used)
    # If path requires auth, we limit by User ID, otherwise by IP
    identifier = request.client.host
    if config.get("auth_required"):
        try:
            # Manually calling the security function since middleware can't use Depends() easily
            identifier = await get_current_user_from_cookie(request)
        except HTTPException:
            # If auth fails on an auth-required path, let the router handle the 401
            pass

    # 3. Sliding Window Logic
    window = config["window"]
    threshold = config["limit"]

    timestamps = rate_limit_store[identifier][path]
    active_requests = [t for t in timestamps if current_time - t < window]
    rate_limit_store[identifier][path] = active_requests

    if len(active_requests) >= threshold:
        logger.warning("rate_limit_exceeded", user_or_ip=identifier, path=path)
        return JSONResponse(
            status_code=429,
            content={"error": "Too Many Requests", "retry_after": f"{window}s"},
        )

    # 4. Proceed
    rate_limit_store[identifier][path].append(current_time)
    return await call_next(request)


@app.get("/health")
async def health_check():
    return {"status": "operational", "active_users_in_limit": len(rate_limit_store)}
