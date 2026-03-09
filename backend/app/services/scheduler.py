"""Scheduler service — handles scheduled extraction runs for all users."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from .. import firebase_client as fb
from .researcher import run_extraction

logger = logging.getLogger(__name__)


def should_run_now(schedule: Dict[str, Any]) -> bool:
    """Determine if a user's schedule should trigger now.

    This is called by the single cron job that runs every hour.
    """
    sched_type = schedule.get("type", "manual")
    if sched_type == "manual":
        return False

    now = datetime.now(timezone.utc)

    if sched_type == "hourly":
        interval = schedule.get("interval_hours", 1)
        # Run if current hour is divisible by interval
        return now.hour % interval == 0

    elif sched_type == "daily":
        target_hour = schedule.get("hour_of_day", 9)
        return now.hour == target_hour

    elif sched_type == "weekly":
        target_day = schedule.get("day_of_week", 0)  # 0=Monday
        target_hour = schedule.get("hour_of_day", 9)
        return now.weekday() == target_day and now.hour == target_hour

    return False


def run_scheduled_extractions() -> Dict[str, Any]:
    """Called by the cron job. Iterates all users with active schedules and runs extraction."""
    users = fb.get_users_with_active_schedules()
    logger.info(f"Checking schedules for {len(users)} users with active schedules.")

    results_summary = {"users_checked": len(users), "users_run": 0, "errors": []}

    for user_data in users:
        uid = user_data.get("uid")
        settings = user_data.get("settings", {})
        schedule = settings.get("schedule", {})

        if not should_run_now(schedule):
            continue

        try:
            sources = fb.list_sources(uid)
            global_keywords = settings.get("global_keywords", [])
            time_window = settings.get("time_window_hours", 3)
            max_trends = settings.get("max_trends_per_source", 3)

            run_extraction(
                uid=uid,
                sources=sources,
                global_keywords=global_keywords,
                time_window_hours=time_window,
                max_trends_per_source=max_trends,
            )
            results_summary["users_run"] += 1
            logger.info(f"Scheduled extraction completed for user {uid}")

        except Exception as e:
            logger.error(f"Scheduled extraction failed for user {uid}: {e}")
            results_summary["errors"].append({"uid": uid, "error": str(e)})

    return results_summary
