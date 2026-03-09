"""Results router — list, filter, export, and delete results."""

import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from ..auth import verify_firebase_token
from ..models import ResultsListResponse, TrendResultResponse
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("", response_model=ResultsListResponse)
async def list_results(
    source_type: Optional[str] = Query(None, description="Filter by source type: reddit, hackernews, bluesky"),
    sort_by: str = Query("created_at", description="Sort field: created_at, trend_score, ups, comments"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    token_data: dict = Depends(verify_firebase_token),
):
    """List results for the authenticated user with filtering and pagination."""
    uid = token_data["uid"]

    results, total = fb.list_results(
        uid=uid,
        source_type=source_type,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return ResultsListResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/export/csv")
async def export_csv(
    token_data: dict = Depends(verify_firebase_token),
):
    """Export all results as CSV download."""
    uid = token_data["uid"]
    results = fb.get_all_results_for_export(uid)

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Timestamp", "Source", "Source Type", "Title", "URL",
        "Description", "Trend Score", "Ups", "Comments",
    ])

    # Data rows
    for r in results:
        created = r.get("created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()

        writer.writerow([
            created,
            r.get("source", ""),
            r.get("source_type", ""),
            r.get("title", ""),
            r.get("url", ""),
            r.get("description", ""),
            r.get("trend_score", 0),
            r.get("ups", 0),
            r.get("comments", 0),
        ])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trends_export.csv"},
    )


@router.delete("/{result_id}", status_code=204)
async def delete_result(
    result_id: str,
    token_data: dict = Depends(verify_firebase_token),
):
    """Delete a single result."""
    uid = token_data["uid"]
    fb.delete_result(uid, result_id)
