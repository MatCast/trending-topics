"""Refactored TrendResearcher for API use. Accepts user source configs directly."""

import logging
from typing import List, Dict, Any

from ..parsers.base import get_parser
from .. import firebase_client as fb

logger = logging.getLogger(__name__)


def run_extraction(
    uid: str,
    sources: List[Dict[str, Any]],
    global_keywords: List[str],
    extraction_id: str,
    time_window_hours: int = 3,
    max_trends_per_source: int = 3,
    use_keywords: bool = True,
) -> Dict[str, Any]:
    """Run trend extraction for a user using their source configs.

    Args:
        uid: Firebase user ID.
        sources: List of source config dicts from Firestore.
        global_keywords: User's global keywords.
        extraction_id: Pre-generated extraction ID.
        time_window_hours: Lookback window.
        max_trends_per_source: Max trends to keep per source.
        use_keywords: Whether to apply keyword filtering.

    Returns:
        Dict with extraction_id, status, results_count, and results list.
    """
    logger.info(f"Starting extraction {extraction_id} for user {uid}")

    try:
        # Get admin config for source weights
        admin_config = fb.get_admin_config()
        source_weights = admin_config.get("source_weights", {})
        retention_days = admin_config.get("default_retention_days", 15)

        # Override with user retention if set
        user_settings = fb.get_user_settings(uid)
        user_retention = user_settings.get("result_retention_days")
        if user_retention:
            retention_days = user_retention

        keywords = global_keywords if use_keywords else []

        # Group results by source
        source_trends: Dict[str, List[Dict[str, Any]]] = {}

        # Only process enabled and valid sources
        enabled_sources = []
        for s in sources:
            if not s.get("enabled", True):
                continue

            sid = s.get("source_id", s.get("type", "unknown"))
            # Safety: if it's reddit, it MUST have a subreddit param
            if sid == "reddit" and not s.get("params", {}).get("subreddit"):
                logger.warning(
                    f"Skipping malformed reddit source for user {uid}: {s.get('id')}"
                )
                continue

            enabled_sources.append(s)

        for source_config in enabled_sources:
            source_type = source_config.get("source_id", source_config.get("type", ""))
            source_name = source_config.get("name", "Unknown")
            params = source_config.get("params", {})
            weight = source_weights.get(source_type, 1.0)

            if source_type == "reddit":
                params["reddit_fetch_method"] = user_settings.get(
                    "reddit_fetch_method", "rapidapi"
                )

            # Determine keywords for this source
            source_keywords = keywords
            if not source_config.get("use_global_keywords", True):
                source_keywords = []

            try:
                parser = get_parser(
                    source_type=source_type,
                    source_name=source_name,
                    time_window_hours=time_window_hours,
                    keywords=source_keywords,
                    weight=weight,
                    params=params,
                )

                trends = parser.fetch()

                if source_name not in source_trends:
                    source_trends[source_name] = []
                source_trends[source_name].extend(trends)

            except Exception as e:
                logger.error(f"Failed to fetch {source_name}: {e}")

        # Deduplicate and select top N per source
        seen_urls = set()
        final_trends = []

        for source_name, trends in source_trends.items():
            trends.sort(key=lambda x: x.get("trend_score", 0), reverse=True)

            selected = 0
            for trend in trends:
                if selected >= max_trends_per_source:
                    break
                url = trend.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    final_trends.append(trend)
                    selected += 1

        # Store results in Firestore
        sources_used = list(
            set(s.get("source_id", s.get("type", "unknown")) for s in enabled_sources)
        )
        fb.store_results(uid, extraction_id, final_trends, sources_used, retention_days)

        logger.info(
            f"Extraction {extraction_id} completed: {len(final_trends)} "
            f"results for user {uid}"
        )

        return {
            "extraction_id": extraction_id,
            "status": "completed",
            "results_count": len(final_trends),
            "results": final_trends,
        }

    except Exception as e:
        logger.error(f"Extraction {extraction_id} failed: {e}")
        fb.update_extraction_status(uid, extraction_id, "failed", str(e))
        return {
            "extraction_id": extraction_id,
            "status": "failed",
            "results_count": 0,
            "results": [],
            "error": str(e),
        }
