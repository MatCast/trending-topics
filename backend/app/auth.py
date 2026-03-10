"""Firebase Auth middleware for FastAPI."""

import logging
from typing import Optional

from fastapi import Request, HTTPException, Depends
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


def get_current_user_uid(token_data: dict = Depends(verify_firebase_token)) -> str:
    """Convenience dependency that returns just the UID."""
    return token_data["uid"]
