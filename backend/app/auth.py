"""Firebase Auth middleware for FastAPI."""

import logging
import os
import secrets

from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify Firebase ID token and return decoded token data.

    Returns a dict with at least: uid, email, name.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email", ""),
            "name": decoded_token.get("name", ""),
        }
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def verify_admin(token_data: dict = Depends(verify_firebase_token)) -> dict:
    """Ensures the authenticated user has an 'admin' active_tier in Firestore."""
    from . import firebase_client as fb

    uid = token_data["uid"]
    user_data = fb.get_user_settings(uid)

    if user_data.get("active_tier") != "admin":
        logger.warning(f"Access denied: User {uid} attempted to access admin route.")
        raise HTTPException(status_code=403, detail="Admin privileges required")

    return token_data


async def verify_internal_api_key(
    x_internal_key: str = Header(None, alias="X-Internal-Key"),
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
) -> bool:
    """Verifies that the request comes from a trusted internal source (Scheduler or API Key)."""
    # 1. Check for X-Internal-Key (Shared Secret)
    expected_key = os.environ.get("INTERNAL_API_KEY")
    if expected_key and x_internal_key and secrets.compare_digest(x_internal_key, expected_key):
        return True

    # 2. Check for X-CloudScheduler (Trusting Cloud Run's header stripping for now)
    if x_cloudscheduler == "true":
        return True

    logger.warning("Unauthorized attempt to access internal/scheduled endpoint.")
    raise HTTPException(status_code=401, detail="Unauthorized")


def get_current_user_uid(token_data: dict = Depends(verify_firebase_token)) -> str:
    """Convenience dependency that returns just the UID."""
    return token_data["uid"]
