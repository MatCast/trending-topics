"""Source configuration CRUD router."""

import logging
from fastapi import APIRouter, Depends, HTTPException

from ..auth import verify_firebase_token
from ..models import SourceConfigCreate, SourceConfigUpdate, SourceConfigResponse
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=list[SourceConfigResponse])
async def list_sources(token_data: dict = Depends(verify_firebase_token)):
    """List all source configs for the authenticated user."""
    uid = token_data["uid"]
    fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))
    sources = fb.list_sources(uid)
    return sources


@router.post("", response_model=SourceConfigResponse, status_code=201)
async def create_source(
    body: SourceConfigCreate,
    token_data: dict = Depends(verify_firebase_token),
):
    """Create a new source configuration."""
    uid = token_data["uid"]
    fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))

    source_data = body.model_dump()
    # Convert enum to string for Firestore
    source_data["type"] = source_data["type"].value if hasattr(source_data["type"], "value") else source_data["type"]

    result = fb.create_source(uid, source_data)
    return result


@router.put("/{source_id}", response_model=SourceConfigResponse)
async def update_source(
    source_id: str,
    body: SourceConfigUpdate,
    token_data: dict = Depends(verify_firebase_token),
):
    """Update an existing source configuration."""
    uid = token_data["uid"]
    update_data = body.model_dump(exclude_none=True)

    if "type" in update_data and hasattr(update_data["type"], "value"):
        update_data["type"] = update_data["type"].value

    # Flatten params for Firestore update
    if "params" in update_data:
        update_data["params"] = update_data["params"].model_dump() if hasattr(update_data["params"], "model_dump") else update_data["params"]

    try:
        result = fb.update_source(uid, source_id, update_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Source not found: {e}")


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: str,
    token_data: dict = Depends(verify_firebase_token),
):
    """Delete a source configuration."""
    uid = token_data["uid"]
    fb.delete_source(uid, source_id)
