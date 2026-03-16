"""Keyword management router."""

import logging
from fastapi import APIRouter, Depends, HTTPException

from ..auth import verify_firebase_token
from ..models import KeywordCreate, KeywordResponse, KeywordBulkAction
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/keywords", tags=["keywords"])


@router.get("", response_model=list[KeywordResponse])
async def list_keywords(token_data: dict = Depends(verify_firebase_token)):
    """List all keywords for the authenticated user."""
    uid = token_data["uid"]
    fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))
    return fb.list_keywords(uid)


@router.post("", response_model=list[KeywordResponse], status_code=201)
async def create_keywords(
    body: KeywordCreate,
    token_data: dict = Depends(verify_firebase_token),
):
    """Create keywords. Accepts a list of strings (comma-split by frontend).
    Trims whitespace, deduplicates (case-insensitive), enforces tier limits.
    """
    uid = token_data["uid"]
    user = fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))
    user_tier = user.get("active_tier", "free")

    created = fb.create_keywords(uid, body.keywords, user_tier=user_tier)
    return created


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: str,
    body: dict,
    token_data: dict = Depends(verify_firebase_token),
):
    """Update a single keyword (e.g., toggle enabled)."""
    uid = token_data["uid"]
    allowed_fields = {"enabled"}
    update_data = {k: v for k, v in body.items() if k in allowed_fields}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    try:
        result = fb.update_keyword(uid, keyword_id, update_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Keyword not found: {e}")


@router.post("/bulk")
async def bulk_action(
    body: KeywordBulkAction,
    token_data: dict = Depends(verify_firebase_token),
):
    """Bulk action on selected keywords: enable, disable, or delete."""
    uid = token_data["uid"]

    if body.action == "enable":
        count = fb.bulk_update_keywords(uid, body.keyword_ids, {"enabled": True})
        return {"action": "enable", "affected": count}
    elif body.action == "disable":
        count = fb.bulk_update_keywords(uid, body.keyword_ids, {"enabled": False})
        return {"action": "disable", "affected": count}
    elif body.action == "delete":
        count = fb.delete_keywords(uid, body.keyword_ids)
        return {"action": "delete", "affected": count}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {body.action}")


@router.delete("/{keyword_id}", status_code=204)
async def delete_keyword(
    keyword_id: str,
    token_data: dict = Depends(verify_firebase_token),
):
    """Delete a single keyword."""
    uid = token_data["uid"]
    fb.delete_keyword(uid, keyword_id)
