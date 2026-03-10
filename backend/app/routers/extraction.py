"""Extraction router — trigger trend extraction for a user."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
import os

from ..auth import verify_firebase_token
from ..models import ExtractionRequest, ExtractionRunResponse
from ..services.researcher import run_extraction
from ..services.scheduler import run_scheduled_extractions
from ..services.cleanup import cleanup_expired
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/extract", tags=["extraction"])


@router.post("", response_model=ExtractionRunResponse)
async def extract(
    body: ExtractionRequest = None,
    token_data: dict = Depends(verify_firebase_token),
):
    """Run trend extraction for the authenticated user."""
    uid = token_data["uid"]
    fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))

    # Get user settings
    settings = fb.get_user_settings(uid)
    sources = fb.list_sources(uid)

    if not sources:
        raise HTTPException(
            status_code=400,
            detail="No sources configured. Please configure at least one source first.",
        )

    # Apply overrides from request body
    time_window = settings.get("time_window_hours", 3)
    max_trends = settings.get("max_trends_per_source", 3)
    use_keywords = True
    global_keywords = fb.list_enabled_keywords(uid)

    if body:
        if body.time_window_hours is not None:
            time_window = body.time_window_hours
        if body.max_trends_per_source is not None:
            max_trends = body.max_trends_per_source
        if body.use_keywords is not None:
            use_keywords = body.use_keywords

    result = run_extraction(
        uid=uid,
        sources=sources,
        global_keywords=global_keywords,
        time_window_hours=time_window,
        max_trends_per_source=max_trends,
        use_keywords=use_keywords,
    )

    return result


@router.post("/scheduled", tags=["internal"])
async def run_scheduled(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
):
    """Internal endpoint called by Cloud Scheduler. Runs extractions for all scheduled users.

    Also triggers cleanup of expired results.
    """
    # Simple auth: check for Cloud Scheduler header or an internal API key
    internal_key = os.environ.get("INTERNAL_API_KEY", "")
    if not x_cloudscheduler and not internal_key:
        logger.warning("Scheduled endpoint called without scheduler header.")
        # In production, you'd want stricter auth here

    # Run scheduled extractions
    extraction_summary = run_scheduled_extractions()

    # Also run cleanup
    cleanup_summary = cleanup_expired()

    return {
        "extraction": extraction_summary,
        "cleanup": cleanup_summary,
    }
