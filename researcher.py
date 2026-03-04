import feedparser
import json
import logging
from datetime import datetime, timedelta, timezone
import time
from typing import List, Dict, Any

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
        In reddit RSS, <content> might contain score but it's hard to parse reliably from standard RSS.
        For simplicity, we use the source_weight and give newer posts higher scores.
        """
        score = source_weight * 10
        # If we could parse upvotes here, we would multiply by upvotes
        return score

    def fetch_trends(self) -> List[Dict[str, Any]]:
        """
        Fetches RSS feeds, filters by time, scores them, and deduplicates against Google Sheets.
        Returns the top 3 trending topics.
        """
        config = self._load_sources()
        reddit_subs = config.get("reddit_subreddits", [])
        rss_feeds = config.get("rss_feeds", [])

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
                    if self._is_within_time_window(entry.get("published_parsed")):
                        score = self._score_trend(entry, source["weight"])
                        all_trends.append(
                            {
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "source": source["name"],
                                "title": entry.get("title", "No Title"),
                                "url": entry.get("link", ""),
                                "description": entry.get("description", ""),
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

        # Sort by trend_score descending and get top 3
        unique_trends.sort(key=lambda x: x["trend_score"], reverse=True)
        top_trends = unique_trends[:3]

        logger.info(f"Found {len(top_trends)} top trending topics after filtering.")
        return top_trends
