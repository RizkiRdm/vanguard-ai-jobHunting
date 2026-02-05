from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.profile.router import router as profile_router
from modules.agent.router import router as agent_router
from dotenv import load_dotenv
import os

# Load ENV
load_dotenv()

app = FastAPI(
    title="Vanguard AI", description="AI Job Hunting Copilot", version="0.1.0"
)

# Mount Static Files (for custom CSS/JS if any)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Templates
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    """
    Initial entry point.
    Redirects to dashboard or login depending on session (To be implemented).
    """
    return templates.TemplateResponse("base.html", {"request": request})


# TODO: Register Routers from modules
# app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(agent_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
