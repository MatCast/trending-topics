import feedparser
import json
import logging
from datetime import datetime, timedelta, timezone
import time
from typing import List, Dict, Any
import requests
import re
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

    def _is_within_time_window_epoch(self, epoch_time: float) -> bool:
        published_dt = datetime.fromtimestamp(epoch_time, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=self.time_window_hours)
        return published_dt >= cutoff

    def _strip_html(self, html_content: str) -> str:
        """Simple regex to strip HTML tags and clean up whitespace."""
        if not html_content:
            return ""

        # Remove script and style elements
        clean = re.sub(
            r"<(script|style).*?>.*?</\1>", "", html_content, flags=re.DOTALL | re.IGNORECASE
        )
        # Strip all other HTML tags
        clean = re.sub(r"<.*?>", " ", clean)
        # Replace multiple spaces/newlines with single space
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def _parse_hn_metrics(self, summary: str) -> Dict[str, int]:
        """Extracts points and comments from HN RSS summary."""
        metrics = {"ups": 0, "comments": 0}
        points_match = re.search(r"Points:\s*(\d+)", summary)
        comments_match = re.search(r"# Comments:\s*(\d+)", summary)

        if points_match:
            metrics["ups"] = int(points_match.group(1))
        if comments_match:
            metrics["comments"] = int(comments_match.group(1))
        return metrics

    def _score_trend(self, ups: int, comments: int, weight: float) -> float:
        """Calculates a trend score based on engagement metrics."""
        return (ups + (comments * 2)) * weight

    def fetch_trends(self, max_trends: int = None) -> List[Dict[str, Any]]:
        """
        Fetches trends from Reddit JSON and Hacker News RSS.
        Returns the top N trending topics PER source type.
        """
        config = self._load_sources()
        reddit_subs = config.get("reddit_subreddits", [])
        rss_feeds = config.get("rss_feeds", [])
        filters = config.get("filters", {})
        keywords = [k.lower() for k in filters.get("keywords", [])]

        if max_trends is None:
            max_trends = int(os.environ.get("MAX_TOP_TRENDS", 3))

        source_trends = {}  # Grouped by source name

        # 1. Fetch Reddit Trends (JSON)
        for sub in reddit_subs:
            source_name = f"r/{sub}"
            source_trends[source_name] = []
            url = f"https://www.reddit.com/r/{sub}/rising.json"
            try:
                # Use a proper User-Agent for Reddit
                headers = {"User-Agent": "LinkedInTrendBot/1.0"}
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    if not self._is_within_time_window_epoch(post.get("created_utc", 0)):
                        continue

                    title = post.get("title", "")
                    # Reddit description is often empty for link posts
                    description = post.get("selftext", "")

                    if keywords:
                        content_lower = (title + " " + description).lower()
                        if not any(k in content_lower for k in keywords):
                            continue

                    ups = post.get("ups", 0)
                    comments = post.get("num_comments", 0)
                    score = self._score_trend(ups, comments, 1.0)

                    source_trends[source_name].append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": source_name,
                            "title": title,
                            "url": f"https://www.reddit.com{post.get('permalink', '')}",
                            "description": description,
                            "trend_score": score,
                            "ups": ups,
                            "comments": comments,
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to fetch Reddit {source_name}: {e}")

        # 2. Fetch RSS Trends (mostly Hacker News)
        for source in rss_feeds:
            source_name = source["name"]
            source_trends[source_name] = []
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries:
                    if not self._is_within_time_window(entry.get("published_parsed")):
                        continue

                    title = entry.get("title", "No Title")
                    raw_summary = entry.get("summary", "")
                    description = self._strip_html(raw_summary)

                    if keywords:
                        content_lower = (title + " " + description).lower()
                        if not any(k in content_lower for k in keywords):
                            continue

                    # Dynamic score parsing based on source
                    ups, comments = 0, 0
                    if "Hacker News" in source_name:
                        hn_metrics = self._parse_hn_metrics(raw_summary)
                        ups = hn_metrics["ups"]
                        comments = hn_metrics["comments"]
                    else:
                        # Fallback for other RSS
                        try:
                            comments = int(entry.get("comments_count", 0))
                        except (ValueError, TypeError):
                            pass

                    score = self._score_trend(ups, comments, source["weight"])
                    source_trends[source_name].append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": source_name,
                            "title": title,
                            "url": entry.get("link", ""),
                            "description": description,
                            "trend_score": score,
                            "ups": ups,
                            "comments": comments,
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to fetch RSS {source_name}: {e}")

        # Final Deduplication and Top N per source selection
        existing_urls = set()
        if self.sheets_manager:
            existing_urls = self.sheets_manager.get_existing_urls()

        final_top_trends = []
        seen_urls = set(existing_urls)

        for source_name, trends in source_trends.items():
            # Sort individual source
            trends.sort(key=lambda x: x["trend_score"], reverse=True)

            source_selected = 0
            for trend in trends:
                if source_selected >= max_trends:
                    break
                if trend["url"] not in seen_urls:
                    seen_urls.add(trend["url"])
                    final_top_trends.append(trend)
                    source_selected += 1

        logger.info(
            f"Filtered to {len(final_top_trends)} top trends total ({max_trends} per source)."
        )
        return final_top_trends
