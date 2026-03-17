"""FastAPI application entry point."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .firebase_client import init_firebase, seed_source_catalog
from .routers import sources, extraction, results, schedule, admin, keywords, extractions, users

# Setup logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Security: Disable docs in production
is_production = os.environ.get("ENV") == "production"

app = FastAPI(
    title="Trend Finder API",
    description="API for finding trending topics across Reddit, Hacker News, and Bluesky.",
    version="1.0.0",
    docs_url=None if is_production else "/api/docs",
    redoc_url=None if is_production else "/api/redoc",
)

# CORS — allow frontend origins
frontend_url_env = os.environ.get("FRONTEND_URL", "http://localhost:3000")
# Support comma-separated origins for multi-environment deployment (local + cloud run)
allowed_origins = [url.strip() for url in frontend_url_env.split(",") if url.strip()]

# Ensure localhost is always allowed in dev-like environments if not explicitly provided
if "http://localhost:3000" not in allowed_origins:
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sources.router)
app.include_router(extraction.router)
app.include_router(extractions.router)
app.include_router(results.router)
app.include_router(schedule.router)
app.include_router(admin.router)
app.include_router(keywords.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup():
    """Initialize Firebase on startup."""
    service_account = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH")
    init_firebase(service_account)
    seed_source_catalog()
    logger.info("Trend Finder API started.")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
