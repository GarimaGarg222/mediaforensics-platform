from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .config import settings
from .database import connect_db, close_db
from .routers import analyze, results, history, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    os.makedirs(settings.upload_dir, exist_ok=True)
    print(f"[App] {settings.app_name} started in {settings.app_env} mode")
    yield
    # Shutdown
    await close_db()
    print("[App] Shutdown complete")


app = FastAPI(
    title="MediaForensics API",
    description="AI-powered media authenticity detection platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (heatmap images) ─────────────
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ── Routers ───────────────────────────────────
app.include_router(analyze.router,  prefix="/api", tags=["Analysis"])
app.include_router(results.router,  prefix="/api", tags=["Results"])
app.include_router(history.router,  prefix="/api", tags=["History"])
app.include_router(reports.router,  prefix="/api", tags=["Reports"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "version": "1.0.0",
    }
