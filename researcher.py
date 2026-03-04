import feedparser
import json
import logging
from datetime import datetime, timedelta, timezone
import time
from typing import List, Dict, Any

import os

logger = logging.getLogger(__name__)


class TrendResearcher:
    def __init__(
        self, sources_file: str, sheets_manager=None, time_window_hours: int = 3
    ):
        self.sources_file = sources_file
        self.sheets_manager = sheets_manager
        self.time_window_hours = time_window_hours

    def _load_sources(self) -> Dict[str, Any]:
        with open(self.sources_file, "r") as f:
            return json.load(f)

    def _is_within_time_window(self, published_parsed: time.struct_time) -> bool:
        if not published_parsed:
            return False

        published_dt = datetime.fromtimestamp(
            time.mktime(published_parsed), tz=timezone.utc
        )
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=self.time_window_hours)
        return published_dt >= cutoff

    def _score_trend(self, entry, source_weight: float) -> float:
        """
        Calculates a trend score based on available metrics.
        Attempts to find upvotes/points/comments in common RSS formats.
        """
        base_score = source_weight * 10

        # Try to find engagement metrics (Reddit, HN, etc often vary)
        # Reddit RSS often doesn't give scores easily, but hnrss provides 'comments' tags
        points = 0

        # hnrss.github.io specifically puts comment counts in the entry
        try:
            # Check for generic 'comments' or custom tags
            comments = int(entry.get("comments", 0))
            points += (comments * 2)
        except Exception:
            pass

        return base_score + points

    def fetch_trends(self, max_trends: int = None) -> List[Dict[str, Any]]:
        """
        Fetches RSS feeds, filters by time, scores them, and deduplicates against Google Sheets.
        Returns the top trending topics.
        """
        config = self._load_sources()
        reddit_subs = config.get("reddit_subreddits", [])
        rss_feeds = config.get("rss_feeds", [])
        filters = config.get("filters", {})
        keywords = [k.lower() for k in filters.get("keywords", [])]

        all_trends = []

        # Build feeds to fetch
        feeds_to_fetch = []
        for sub in reddit_subs:
            feeds_to_fetch.append(
                {
                    "name": f"r/{sub}",
                    "url": f"https://www.reddit.com/r/{sub}/rising.rss",
                    "weight": 1.0,
                }
            )

        for feed in rss_feeds:
            feeds_to_fetch.append(feed)

        logger.info(f"Fetching {len(feeds_to_fetch)} feeds...")

        # Fetch and filter
        for source in feeds_to_fetch:
            try:
                feed = feedparser.parse(source["url"])
                if feed.bozo:
                    logger.warning(
                        f"Error parsing feed {source['name']}: {feed.bozo_exception}"
                    )
                    continue

                for entry in feed.entries:
                    title = entry.get("title", "No Title")
                    description = entry.get("description", "")

                    # 1. Time Filter
                    if not self._is_within_time_window(entry.get("published_parsed")):
                        continue

                    # 2. Keyword Filter (Targeting AI trends)
                    if keywords:
                        content_lower = (title + " " + description).lower()
                        if not any(k in content_lower for k in keywords):
                            continue

                    score = self._score_trend(entry, source["weight"])
                    all_trends.append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": source["name"],
                            "title": title,
                            "url": entry.get("link", ""),
                            "description": description,
                            "trend_score": score,
                            "published_parsed": entry.get("published_parsed"),
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to fetch {source['name']}: {e}")

        # Deduplicate globally by URL (and against existing sheet)
        existing_urls = set()
        if self.sheets_manager:
            existing_urls = self.sheets_manager.get_existing_urls()

        unique_trends = []
        seen_urls = set(existing_urls)

        for trend in all_trends:
            if trend["url"] not in seen_urls:
                seen_urls.add(trend["url"])
                unique_trends.append(trend)

        # Sort by trend_score descending and get top trends limit from param or env
        unique_trends.sort(key=lambda x: x["trend_score"], reverse=True)

        if max_trends is None:
            max_trends = int(os.environ.get("MAX_TOP_TRENDS", 3))

        top_trends = unique_trends[:max_trends]

        logger.info(f"Found {len(top_trends)} top trending topics after filtering.")
        return top_trends
