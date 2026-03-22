"""User profile and settings router."""

import logging
from fastapi import APIRouter, Depends

from ..auth import verify_firebase_token
from ..models import UserProfileResponse
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(token_data: dict = Depends(verify_firebase_token)):
    """Get the current authenticated user's profile and tier limits."""
    uid = token_data["uid"]

    # Get or create user to ensure core data exists
    user_data = fb.get_or_create_user(
        uid, token_data.get("email", ""), token_data.get("name", "")
    )

    tier = user_data.get("active_tier", "free")

    # Fetch limits dynamically from Firestore
    kw_limit = fb.get_keyword_limit(tier)
    reddit_limit = fb.get_reddit_source_limit(tier)
    extraction_limits = fb.get_extraction_limits(tier)

    return {
        "uid": uid,
        "email": user_data.get("email", ""),
        "active_tier": tier,
        "tier_limits": {
            "keywords": kw_limit,
            "reddit_sources": reddit_limit,
            "extractions": extraction_limits,
        },
        "usage": {
            "extractions": fb.get_user_extraction_usage(uid),
        },
        "settings": user_data.get("settings", {}),
    }
