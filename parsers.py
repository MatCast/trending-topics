import requests
import os
import feedparser
import re
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TrendParser:
    """Base class for all source parsers."""

    def __init__(
        self, source_config: Dict[str, Any], time_window_hours: int, keywords: List[str]
    ):
        self.config = source_config
        self.time_window_hours = time_window_hours
        self.keywords = [k.lower() for k in keywords]
        self.weight = self.config.get("weight", 1.0)
        self.source_name = self.config.get("name", "Unknown Source")

    def fetch(self) -> List[Dict[str, Any]]:
        """Must be implemented by subclasses. Returns a list of standardized trend dictionaries."""
        raise NotImplementedError

    def _score_trend(self, ups: int, comments: int) -> float:
        return (ups + (comments * 2)) * self.weight

    def _passes_keywords(self, text: str) -> bool:
        if not self.keywords:
            return True
        text_lower = text.lower()
        return any(k in text_lower for k in self.keywords)


class RedditParser(TrendParser):
    def fetch(self) -> List[Dict[str, Any]]:
        logger.info(f"Fetching trends from Reddit: {self.source_name}...")
        trends = []
        subreddit = self.config.get("subreddit")
        if not subreddit:
            logger.error(f"RedditParser missing 'subreddit' in config: {self.config}")
            return []

        # Create a dynamic source name if not explicitly provided
        if self.source_name == "Unknown Source":
            self.source_name = f"r/{subreddit}"

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

                trends.append(
                    {
                        "timestamp": now.isoformat(),
                        "source": self.source_name,
                        "title": title,
                        "url": f"https://www.reddit.com{post.get('permalink', '')}",
                        "description": description,
                        "trend_score": score,
                        "ups": ups,
                        "comments": comments,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to fetch Reddit {self.source_name}: {e}")

        return trends


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
        logger.info(f"Fetching trends from Hacker News: {self.source_name}...")
        trends = []
        url = self.config.get("url")
        if not url:
            logger.error(f"HackerNewsParser missing 'url' in config: {self.config}")
            return []

        try:
            feed = feedparser.parse(url)

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            for entry in feed.entries:
                # Time filter
                published_parsed = entry.get("published_parsed")
                if not published_parsed:
                    continue

                import time

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

                # HN Metric parsing
                ups, comments = 0, 0
                points_match = re.search(r"Points:\s*(\d+)", raw_summary)
                comments_match = re.search(r"# Comments:\s*(\d+)", raw_summary)
                if points_match:
                    ups = int(points_match.group(1))
                if comments_match:
                    comments = int(comments_match.group(1))

                score = self._score_trend(ups, comments)

                # HN Thread URL
                entry_url = entry.get("link", "")
                if entry.get("comments"):
                    entry_url = entry.get("comments")

                trends.append(
                    {
                        "timestamp": now.isoformat(),
                        "source": self.source_name,
                        "title": title,
                        "url": entry_url,
                        "description": description,
                        "trend_score": score,
                        "ups": ups,
                        "comments": comments,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to fetch HN {self.source_name}: {e}")

        return trends


class BlueskyParser(TrendParser):
    def __init__(self, source_config: Dict[str, Any], time_window_hours: int, keywords: List[str]):
        super().__init__(source_config, time_window_hours, keywords)
        self.handle = os.environ.get("BLUESKY_HANDLE")
        self.password = os.environ.get("BLUESKY_APP_PASSWORD")
        self.session = None

    def _create_session(self):
        """Authenticates with Bluesky to get a JWT."""
        if not self.handle or not self.password:
            logger.warning("Bluesky credentials missing. Search might be restricted or fail.")
            return None

        url = "https://bsky.social/xrpc/com.atproto.server.createSession"
        try:
            resp = requests.post(url, json={"identifier": self.handle, "password": self.password}, timeout=10)
            resp.raise_for_status()
            self.session = resp.json()
            return self.session
        except Exception as e:
            logger.error(f"Bluesky auth failed: {e}")
            return None

    def fetch(self) -> List[Dict[str, Any]]:
        logger.info(f"Fetching trends from Bluesky: {self.source_name}...")
        trends = []

        # 1. Authenticate if possible
        if not self.session:
            self._create_session()

        # Use the primary bsky.social endpoint for searched results
        url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"

        query = " OR ".join(self.keywords) if self.keywords else "AI"
        params = {
            "q": query,
            "sort": "top",
            "limit": 50
        }

        headers = {"User-Agent": "LinkedInTrendBot/2.0"}
        if self.session:
            headers["Authorization"] = f"Bearer {self.session.get('accessJwt')}"

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            for post_item in data.get("posts", []):
                record = post_item.get("record", {})

                created_at_str = record.get("createdAt")
                if not created_at_str: continue

                created_at_str = created_at_str.replace("Z", "+00:00")
                try:
                    created_dt = datetime.fromisoformat(created_at_str)
                    if created_dt < cutoff:
                        continue
                except ValueError:
                    continue

                text = record.get("text", "")
                if not self._passes_keywords(text):
                    continue

                ups = post_item.get("likeCount", 0)
                comments = post_item.get("replyCount", 0) + post_item.get("repostCount", 0)
                score = self._score_trend(ups, comments)

                author_handle = post_item.get("author", {}).get("handle")
                uri = post_item.get("uri", "")
                post_id = uri.split("/")[-1] if uri else ""

                post_url = ""
                if author_handle and post_id:
                    post_url = f"https://bsky.app/profile/{author_handle}/post/{post_id}"

                trends.append({
                    "timestamp": now.isoformat(),
                    "source": self.source_name,
                    "title": f"Post by @{author_handle}",
                    "url": post_url,
                    "description": text,
                    "trend_score": score,
                    "ups": ups,
                    "comments": comments,
                })
        except Exception as e:
            logger.error(f"Failed to fetch Bluesky {self.source_name}: {e}")

        return trends


# Factory function to get the right parser
def get_parser(
    source_config: Dict[str, Any], time_window_hours: int, keywords: List[str]
) -> TrendParser:
    source_type = source_config.get("type", "").lower()
    if source_type == "reddit":
        return RedditParser(source_config, time_window_hours, keywords)
    elif source_type == "hackernews":
        return HackerNewsParser(source_config, time_window_hours, keywords)
    elif source_type == "bluesky":
        return BlueskyParser(source_config, time_window_hours, keywords)
    else:
        raise ValueError(
            f"Unknown source type: '{source_type}' in config: {source_config}"
        )
