"""Hacker News parser — fetches top stories via RSS."""

import logging
import re
import time
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from .base import TrendParser

logger = logging.getLogger(__name__)

HN_TOP_RSS = "https://hnrss.org/newest?points=10"


class HackerNewsParser(TrendParser):
    def _strip_html(self, html_content: str) -> str:
        if not html_content:
            return ""
        clean = re.sub(
            r"<(script|style).*?>.*?</\1>",
            "",
            html_content,
            flags=re.DOTALL | re.IGNORECASE,
        )
        clean = re.sub(r"<.*?>", " ", clean)
        return re.sub(r"\s+", " ", clean).strip()

    def fetch(self) -> List[Dict[str, Any]]:
        url = self.params.get("url") or HN_TOP_RSS
        logger.info(f"Fetching trends from Hacker News: {self.source_name}...")
        trends = []

        try:
            feed = feedparser.parse(url)

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            for entry in feed.entries:
                published_parsed = entry.get("published_parsed")
                if not published_parsed:
                    continue

                published_dt = datetime.fromtimestamp(
                    time.mktime(published_parsed), tz=timezone.utc
                )
                if published_dt < cutoff:
                    continue

                title = entry.get("title", "No Title")
                raw_summary = entry.get("summary", "")
                description = self._strip_html(raw_summary)

                if not self._passes_keywords(title + " " + description):
                    continue

                # HN metric parsing
                ups, comments = 0, 0
                points_match = re.search(r"Points:\s*(\d+)", raw_summary)
                comments_match = re.search(r"# Comments:\s*(\d+)", raw_summary)
                if points_match:
                    ups = int(points_match.group(1))
                if comments_match:
                    comments = int(comments_match.group(1))

                score = self._score_trend(ups, comments)

                entry_url = entry.get("link", "")
                if entry.get("comments"):
                    entry_url = entry.get("comments")

                trends.append({
                    "timestamp": now.isoformat(),
                    "source": self.source_name,
                    "source_type": "hackernews",
                    "title": title,
                    "url": entry_url,
                    "description": description,
                    "trend_score": score,
                    "ups": ups,
                    "comments": comments,
                })
        except Exception as e:
            logger.error(f"Failed to fetch HN {self.source_name}: {e}")

        return trends
