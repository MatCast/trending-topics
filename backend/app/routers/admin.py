"""Admin router — global configuration management."""

import logging
from fastapi import APIRouter, Depends

from ..auth import verify_admin
from ..models import AdminConfig, AdminConfigUpdate
from .. import firebase_client as fb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/config", response_model=AdminConfig)
async def get_admin_config(token_data: dict = Depends(verify_admin)):
    """Get global admin configuration (source weights, retention defaults)."""
    config = fb.get_admin_config()
    return config


@router.put("/config", response_model=AdminConfig)
async def update_admin_config(
    body: AdminConfigUpdate,
    token_data: dict = Depends(verify_admin),
):
    """Update global admin configuration."""
    update_data = body.model_dump(exclude_none=True)
    result = fb.update_admin_config(update_data)
    return result
