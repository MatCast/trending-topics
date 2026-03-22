"""Schedule router — manage user's extraction schedule."""

import logging
from fastapi import APIRouter, Depends

from ..auth import verify_firebase_token
from ..models import UserSettingsUpdate, UserSettingsResponse
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=UserSettingsResponse)
async def get_settings(token_data: dict = Depends(verify_firebase_token)):
    """Get user settings including schedule."""
    uid = token_data["uid"]
    fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))
    settings = fb.get_user_settings(uid)
    return settings


@router.put("", response_model=UserSettingsResponse)
async def update_settings(
    body: UserSettingsUpdate,
    token_data: dict = Depends(verify_firebase_token),
):
    """Update user settings (global keywords, time window, schedule, etc.)."""
    uid = token_data["uid"]
    fb.get_or_create_user(uid, token_data.get("email", ""), token_data.get("name", ""))

    update_data = body.model_dump(exclude_none=True)

    # Convert schedule to dict for Firestore
    if "schedule" in update_data and hasattr(update_data["schedule"], "model_dump"):
        update_data["schedule"] = update_data["schedule"].model_dump()

    result = fb.update_user_settings(uid, update_data)
    return result
