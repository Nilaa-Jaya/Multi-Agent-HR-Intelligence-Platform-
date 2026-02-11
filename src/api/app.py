"""
FastAPI application for Multi-Agent HR Intelligence Platform
Production-ready web interface
Version: 3.0.0
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

from src.api.routes import router
from src.api.webhooks import router as webhooks_router
from src.database import init_db
from src.utils import app_logger

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent HR Intelligence Platform",
    description="Intelligent Customer Support Agent with KB Integration",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API routes
app.include_router(router)
app.include_router(webhooks_router, tags=["Webhooks"])


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    app_logger.info("Starting Multi-Agent HR Intelligence Platform FastAPI application...")

    try:
        # Initialize database
        init_db()
        app_logger.info("Database initialized successfully")
    except Exception as e:
        app_logger.warning(f"Database initialization warning: {e}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI"""
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Multi-Agent HR Intelligence Platform"}
    )


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok"}


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    app_logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run(
        "src.api.app:app", host=host, port=port, reload=reload, log_level="info"
    )


if __name__ == "__main__":
    run_server()
