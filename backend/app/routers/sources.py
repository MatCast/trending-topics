"""Source configuration CRUD router."""

import logging
from fastapi import APIRouter, Depends, HTTPException

from ..auth import verify_firebase_token
from ..models import (
    SourceConfigCreate,
    SourceConfigUpdate,
    SourceConfigResponse,
    SourceCatalogEntry,
)
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("/catalog", response_model=list[SourceCatalogEntry])
async def list_catalog(token_data: dict = Depends(verify_firebase_token)):
    """List all available sources from the catalog."""
    # For now, all users see 'public' sources. Tier filtering future-proofed.
    catalog = fb.list_catalog_sources(user_tier="free")
    return catalog


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
    """Create a new source subscription."""
    uid = token_data["uid"]
    user = fb.get_or_create_user(
        uid, token_data.get("email", ""), token_data.get("name", "")
    )
    source_data = body.model_dump()
    user_tier = user.get("active_tier", "free")

    try:
        result = fb.create_source(uid, source_data, user_tier=user_tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@router.put("/{source_id}", response_model=SourceConfigResponse)
async def update_source(
    source_id: str,
    body: SourceConfigUpdate,
    token_data: dict = Depends(verify_firebase_token),
):
    """Update an existing source configuration."""
    uid = token_data["uid"]
    user = fb.get_or_create_user(
        uid, token_data.get("email", ""), token_data.get("name", "")
    )
    update_data = body.model_dump(exclude_none=True)
    user_tier = user.get("active_tier", "free")

    try:
        result = fb.update_source(uid, source_id, update_data, user_tier=user_tier)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update source {source_id}: {e}")
        raise HTTPException(status_code=404, detail="Source not found")


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: str,
    token_data: dict = Depends(verify_firebase_token),
):
    """Delete a source configuration."""
    uid = token_data["uid"]
    fb.delete_source(uid, source_id)
