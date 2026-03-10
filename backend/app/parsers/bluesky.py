"""Bluesky parser — searches posts via Bluesky API."""

import logging
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from .base import TrendParser

logger = logging.getLogger(__name__)


class BlueskyParser(TrendParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handle = os.environ.get("BLUESKY_HANDLE")
        self.password = os.environ.get("BLUESKY_APP_PASSWORD")
        self.session = None

    def _create_session(self):
        """Authenticates with Bluesky to get a JWT."""
        if not self.handle or not self.password:
            logger.warning("Bluesky credentials missing. Search might be restricted.")
            return None

        url = "https://bsky.social/xrpc/com.atproto.server.createSession"
        try:
            resp = requests.post(
                url,
                json={"identifier": self.handle, "password": self.password},
                timeout=10,
            )
            resp.raise_for_status()
            self.session = resp.json()
            return self.session
        except Exception as e:
            logger.error(f"Bluesky auth failed: {e}")
            return None

    def fetch(self) -> List[Dict[str, Any]]:
        logger.info(f"Fetching trends from Bluesky: {self.source_name}...")
        trends = []

        if not self.session:
            self._create_session()

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=self.time_window_hours)

        url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"

        headers = {"User-Agent": "TrendingNews/2.0"}
        if self.session:
            headers["Authorization"] = f"Bearer {self.session.get('accessJwt')}"

        queries = self.keywords if self.keywords else ["AI"]
        all_posts = {}

        for query in queries:
            params = {
                "q": query,
                "sort": "top",
                "limit": 30,
                "since": cutoff.isoformat().replace("+00:00", "Z")
            }

            try:
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                for post_item in data.get("posts", []):
                    uri = post_item.get("uri")
                    if uri not in all_posts:
                        all_posts[uri] = post_item
            except Exception as e:
                logger.error(f"Failed to fetch Bluesky for query '{query}': {e}")

        for post_item in all_posts.values():
            record = post_item.get("record", {})

            created_at_str = record.get("createdAt")
            if not created_at_str:
                continue

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
                "source_type": "bluesky",
                "title": f"Post by @{author_handle}",
                "url": post_url,
                "description": text,
                "trend_score": score,
                "ups": ups,
                "comments": comments,
            })

        return trends
