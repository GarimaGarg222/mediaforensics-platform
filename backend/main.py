from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .config import settings
from .database import connect_db, close_db, get_collection
from .routers import analyze, results, history, reports
from .routers import auth as auth_router


async def create_indexes():
    """Create MongoDB indexes for performance."""
    jobs = get_collection("jobs")
    await jobs.create_index("job_id", unique=True)
    await jobs.create_index("created_at")
    await jobs.create_index("result.verdict")
    await jobs.create_index("user_id")

    users = get_collection("users")
    await users.create_index("email", unique=True)
    await users.create_index("user_id", unique=True)

    print("[DB] MongoDB indexes created")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    await create_indexes()
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs("./reports", exist_ok=True)
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

# ── Static files ──────────────────────────────
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ── Routers ───────────────────────────────────
app.include_router(auth_router.router, prefix="/api", tags=["Auth"])
app.include_router(analyze.router,     prefix="/api", tags=["Analysis"])
app.include_router(results.router,     prefix="/api", tags=["Results"])
app.include_router(history.router,     prefix="/api", tags=["History"])
app.include_router(reports.router,     prefix="/api", tags=["Reports"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "version": "1.0.0",
    }
