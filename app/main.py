import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db, get_db_connection
from app.routers import issues

# Lifespan event handler for startup/shutdown tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure SQLite tables and indexes exist on application startup
    init_db()
    yield
    # Any teardown logic can be placed here if needed


app = FastAPI(
    title="IssueTrack – Smart Bug & Issue Tracking API",
    description=(
        "Production-grade, lightweight REST API for tracking software bugs, tasks, "
        "and development workflows. Built with FastAPI, SQLite, and Pydantic."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for local development and client integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Issue API routes
app.include_router(issues.router)

# Ensure static directory exists and mount it for assets
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", tags=["Health"], summary="Service Healthcheck")
def health_check():
    """Validates API health and database connectivity."""
    db_ok = False
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1;")
        conn.close()
        db_ok = True
    except Exception as e:
        db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "IssueTrack API",
        "database": "connected" if db_ok else "unreachable"
    }


@app.get("/", tags=["Dashboard"], summary="Serve Dashboard UI")
def serve_dashboard():
    """Serves the frontend dashboard index.html if present, else JSON info."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "Welcome to IssueTrack API",
        "docs": "/docs",
        "health": "/health",
        "issues_api": "/api/issues"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches unhandled exceptions and returns a clean, structured JSON response
    without leaking internal stack traces.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request.",
            "detail": str(exc)
        }
    )

