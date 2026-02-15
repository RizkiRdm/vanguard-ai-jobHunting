import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from shadow_logger import setup_logging
from dotenv import load_dotenv

# IMPORT ROUTERS
from modules.profile.router import router as profile_router
from modules.agent.router import router as agent_router
from core.browser_engine import browser_engine

# Load environment variables
load_dotenv()

# Konfigurasi Logging Dasar
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VanguardMain")

app = FastAPI(
    title="Vanguard AI",
    description="AI Job Hunting Copilot - Autonomous Job Application Suite",
    version="1.0.0",
)

# --- MIDDLEWARE ---
# Mengizinkan akses jika nantinya kita memisahkan frontend atau menggunakan port berbeda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STATIC & TEMPLATES ---
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("static/screenshots"):
    os.makedirs("static/screenshots")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- LIFECYCLE EVENTS ---
@app.on_event("startup")
async def startup_event():
    logger.info("Vanguard AI is starting up...")
    # Browser engine bisa di-warmup di sini jika perlu


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Vanguard AI...")
    # Memastikan browser playwright tertutup dengan bersih saat server mati
    await browser_engine.close()


# --- GLOBAL ERROR HANDLER ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Terjadi kesalahan internal pada sistem Vanguard.",
            "detail": str(exc),
        },
    )


# --- ROUTER REGISTRATION ---
app.include_router(profile_router)
app.include_router(agent_router)

# --- CORE ROUTES ---


@app.get("/")
async def root(request: Request):
    """
    Landing page / Entry point.
    Langsung menampilkan Dashboard untuk user experience yang lebih cepat.
    """
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    """
    Halaman utama monitoring.
    Menampilkan status agen, log terbaru, dan statistik penggunaan.
    """
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


@app.get("/health")
async def health_check():
    """Endpoint untuk memastikan server berjalan (untuk monitoring/docker)"""
    return {"status": "healthy", "engine": "Vanguard-1.0"}


if __name__ == "__main__":
    import uvicorn

    # Menjalankan aplikasi
    logger.info("Launching Uvicorn Server...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
