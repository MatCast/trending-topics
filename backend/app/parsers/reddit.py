"""Reddit parser — fetches rising posts from subreddits."""

import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from .base import TrendParser

logger = logging.getLogger(__name__)


class RedditParser(TrendParser):
    def fetch(self) -> List[Dict[str, Any]]:
        subreddit = self.params.get("subreddit")
        if not subreddit:
            logger.error(f"RedditParser missing 'subreddit' param for {self.source_name}")
            return []

        logger.info(f"Fetching trends from Reddit: {self.source_name} (r/{subreddit})...")
        trends = []
        url = f"https://www.reddit.com/r/{subreddit}/rising.json"

        try:
            headers = {"User-Agent": "LinkedInTrendBot/2.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})

                # Time filter
                created_dt = datetime.fromtimestamp(
                    post.get("created_utc", 0), tz=timezone.utc
                )
                if created_dt < cutoff:
                    continue

                title = post.get("title", "")
                description = post.get("selftext", "")

                # Keyword filter
                if not self._passes_keywords(title + " " + description):
                    continue

                ups = post.get("ups", 0)
                comments = post.get("num_comments", 0)
                score = self._score_trend(ups, comments)

                trends.append({
                    "timestamp": now.isoformat(),
                    "source": self.source_name,
                    "source_type": "reddit",
                    "title": title,
                    "url": f"https://www.reddit.com{post.get('permalink', '')}",
                    "description": description,
                    "trend_score": score,
                    "ups": ups,
                    "comments": comments,
                })
        except Exception as e:
            logger.error(f"Failed to fetch Reddit {self.source_name}: {e}")

        return trends
