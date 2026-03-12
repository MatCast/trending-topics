"""FastAPI application entry point."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .firebase_client import init_firebase, seed_source_catalog
from .routers import sources, extraction, results, schedule, admin, keywords, extractions

# Setup logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trend Finder API",
    description="API for finding trending topics across Reddit, Hacker News, and Bluesky.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS — allow frontend origin
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
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
