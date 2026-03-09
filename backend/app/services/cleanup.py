"""Cleanup service — removes expired results."""

import logging
from .. import firebase_client as fb

logger = logging.getLogger(__name__)


def cleanup_expired():
    """Delete all expired results. Called by cron or on demand."""
    count = fb.cleanup_expired_results()
    logger.info(f"Cleanup completed: {count} expired results deleted.")
    return {"deleted_count": count}
