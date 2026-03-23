import logging
from fastapi import APIRouter, Depends, Query

from ..auth import verify_firebase_token
from ..models import ExtractionListResponse, ExtractionResponse
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/extractions", tags=["extractions"])


@router.get("", response_model=ExtractionListResponse)
async def list_extractions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    token_data: dict = Depends(verify_firebase_token),
):
    """List extraction history for the authenticated user."""
    uid = token_data["uid"]

    extractions, total = fb.list_extractions(
        uid=uid,
        page=page,
        page_size=page_size,
    )

    return ExtractionListResponse(
        extractions=extractions,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{extraction_id}", response_model=ExtractionResponse)
async def get_extraction(
    extraction_id: str,
    token_data: dict = Depends(verify_firebase_token),
):
    """Get details for a specific extraction run."""
    uid = token_data["uid"]
    extraction = fb.get_extraction(uid, extraction_id)

    if not extraction:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Extraction not found")

    return ExtractionResponse(**extraction)
