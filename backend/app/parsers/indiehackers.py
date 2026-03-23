"""Indie Hackers parser — fetches top stories via unofficial RSS."""

import logging
import re
import time
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from .base import TrendParser

logger = logging.getLogger(__name__)

IH_TOP_RSS = "https://feed.indiehackers.world/posts.rss"


class IndieHackersParser(TrendParser):
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
        url = self.params.get("url") or IH_TOP_RSS
        logger.info(f"Fetching trends from Indie Hackers: {self.source_name}...")
        trends = []

        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                self.add_insight("info", "Source API returned 0 items.")
                return []

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            filtered_count = 0
            for entry in feed.entries:
                published_parsed = entry.get("published_parsed")
                if not published_parsed:
                    # Try getting from updated_parsed if published_parsed is missing
                    published_parsed = entry.get("updated_parsed")

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
                    filtered_count += 1
                    continue

                # The unofficial feed doesn't consistently provide ups/comments in
                # standard fields. We will give it a modest default score to ensure
                # it appears if it matches keywords, or attempt to parse if the
                # community feed adds it later.
                ups, comments = 10, 0

                # Attempt to extract some stats if they exist in summary
                # (unlikely but good to have)
                points_match = re.search(r"(\d+)\s+points?", raw_summary, re.IGNORECASE)
                comments_match = re.search(
                    r"(\d+)\s+comments?", raw_summary, re.IGNORECASE
                )
                if points_match:
                    ups = int(points_match.group(1))
                if comments_match:
                    comments = int(comments_match.group(1))

                score = self._score_trend(ups, comments)

                entry_url = entry.get("link", "")

                trends.append(
                    {
                        "timestamp": now.isoformat(),
                        "source": self.source_name,
                        "source_type": "indiehackers",
                        "title": title,
                        "url": entry_url,
                        "description": description,
                        "trend_score": score,
                        "ups": ups,
                        "comments": comments,
                    }
                )
            if filtered_count > 0:
                self.add_insight(
                    "warning", f"{filtered_count} posts filtered out by keywords."
                )

        except Exception as e:
            msg = f"Failed to fetch Indie Hackers {self.source_name}: {e}"
            logger.error(msg)
            self.add_insight("error", msg)

        return trends
