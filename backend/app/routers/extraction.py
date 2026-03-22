"""Extraction router — trigger trend extraction for a user."""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from ..auth import verify_firebase_token, verify_internal_api_key
from ..models import ExtractionRequest, ExtractionRunResponse
from ..services.researcher import run_extraction
from ..services.scheduler import run_scheduled_extractions
from ..services.cleanup import cleanup_expired
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/extract", tags=["extraction"])


@router.post("", response_model=ExtractionRunResponse)
async def extract(
    background_tasks: BackgroundTasks,
    body: ExtractionRequest = None,
    token_data: dict = Depends(verify_firebase_token),
):
    """Run trend extraction for the authenticated user."""
    uid = token_data["uid"]
    user_data = fb.get_or_create_user(
        uid, token_data.get("email", ""), token_data.get("name", "")
    )
    user_tier = user_data.get("active_tier", "free")

    # 1. Enforce Concurrency (Max 1 at a time)
    if fb.has_active_extraction(uid):
        logger.warning(f"User {uid} attempted concurrent extraction.")
        raise HTTPException(
            status_code=400,
            detail="You already have an extraction in progress. Please wait for it to finish.",
        )

    # 2. Enforce Volume Quota (Daily/Weekly/Monthly)
    success, limit_period = fb.check_and_increment_extraction_quota(uid, user_tier)
    if not success:
        logger.warning(
            f"User {uid} ({user_tier}) reached {limit_period} extraction limit."
        )
        raise HTTPException(
            status_code=429,
            detail=f"You have reached your {limit_period} extraction limit. Upgrade your tier for more!",
        )

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

    # Generate sources_used for the pending doc
    # Generate sources_used for the pending doc
    # Robust filtering: only include enabled sources, and for multi-instance (like reddit), require params
    enabled_sources = []
    for s in sources:
        if not s.get("enabled", True):
            continue

        sid = s.get("source_id", s.get("type", "unknown"))
        # Safety: if it's reddit, it MUST have a subreddit param
        if sid == "reddit" and not s.get("params", {}).get("subreddit"):
            logger.warning(
                f"Skipping malformed reddit source for user {uid}: {s.get('id')}"
            )
            continue

        enabled_sources.append(s)

    sources_used = list(
        set(s.get("source_id", s.get("type", "unknown")) for s in enabled_sources)
    )
    # Create the pending extraction document
    extraction_id = fb.create_pending_extraction(uid, sources_used)

    # Add to background tasks
    background_tasks.add_task(
        run_extraction,
        uid=uid,
        sources=sources,
        global_keywords=global_keywords,
        extraction_id=extraction_id,
        time_window_hours=time_window,
        max_trends_per_source=max_trends,
        use_keywords=use_keywords,
    )

    return {
        "extraction_id": extraction_id,
        "status": "pending",
        "results_count": 0,
        "results": [],
    }


@router.post("/scheduled", tags=["internal"])
async def run_scheduled(
    authorized: bool = Depends(verify_internal_api_key),
):
    """Internal endpoint called by Cloud Scheduler. Runs extractions for all scheduled users.

    Also triggers cleanup of expired results.
    """
    # Run scheduled extractions
    extraction_summary = run_scheduled_extractions()

    # Also run cleanup
    cleanup_summary = cleanup_expired()

    return {
        "extraction": extraction_summary,
        "cleanup": cleanup_summary,
    }
