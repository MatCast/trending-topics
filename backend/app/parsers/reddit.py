"""Reddit parser — fetches rising posts from subreddits."""

import logging
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from .base import TrendParser

logger = logging.getLogger(__name__)


class RedditParser(TrendParser):
    def fetch(self) -> List[Dict[str, Any]]:
        subreddit = self.params.get("subreddit")
        if not subreddit:
            logger.error(
                f"RedditParser missing 'subreddit' param for {self.source_name}"
            )
            return []

        fetch_method = self.params.get("reddit_fetch_method", "rapidapi")
        logger.info(
            f"Fetching trends from Reddit ({fetch_method}): {self.source_name} (r/{subreddit})..."
        )

        if fetch_method == "rapidapi":
            return self._fetch_rapidapi(subreddit)
        else:
            return self._fetch_direct(subreddit)

    def _fetch_rapidapi(self, subreddit: str) -> List[Dict[str, Any]]:
        trends = []
        rapidapi_key = os.environ.get("RAPIDAPI_KEY")
        if not rapidapi_key:
            logger.error(
                "RAPIDAPI_KEY environment variable is not set. Falling back to direct fetch."
            )
            return self._fetch_direct(subreddit)

        url = "https://reddit3.p.rapidapi.com/v1/reddit/posts"
        querystring = {
            "url": f"https://www.reddit.com/r/{subreddit}/",
            "filter": "rising",
        }
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "reddit3.p.rapidapi.com",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.get(url, headers=headers, params=querystring, timeout=10)
            resp.raise_for_status()

            # Log and track credits if available
            remaining = resp.headers.get("X-RateLimit-Requests-Remaining")
            if remaining:
                logger.info(f"RapidAPI Credits Remaining: {remaining}")
                try:
                    from .. import firebase_client as fb
                    fb.update_api_usage("rapidapi_reddit", int(remaining), resp.headers.get("X-RateLimit-Requests-Reset"))
                except Exception as e:
                    logger.error(f"Failed to update API usage in Firebase: {e}")

            data = resp.json()

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            for post in data.get("body", []):
                created_dt = datetime.fromtimestamp(
                    post.get("created_utc", 0), tz=timezone.utc
                )
                if created_dt < cutoff:
                    continue

                title = post.get("title", "")
                description = post.get("selftext", "")

                if not self._passes_keywords(title + " " + description):
                    continue

                ups = post.get("ups", 0)
                comments = post.get("num_comments", 0)
                score = self._score_trend(ups, comments)

                trends.append(
                    {
                        "timestamp": now.isoformat(),
                        "source": self.source_name,
                        "source_type": "reddit",
                        "title": title,
                        "url": f"https://www.reddit.com{post.get('permalink', '')}",
                        "description": description,
                        "trend_score": score,
                        "ups": ups,
                        "comments": comments,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to fetch Reddit RapidAPI {self.source_name}: {e}")
            logger.info("Falling back to direct Reddit fetch method...")
            return self._fetch_direct(subreddit)

        return trends

    def _fetch_direct(self, subreddit: str) -> List[Dict[str, Any]]:
        trends = []
        url = f"https://www.reddit.com/r/{subreddit}/rising.json"

        try:
            # Emulate a real browser to bypass strict IP/bot filters on Reddit
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "application/json",
            }
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.time_window_hours)

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})

                created_dt = datetime.fromtimestamp(
                    post.get("created_utc", 0), tz=timezone.utc
                )
                if created_dt < cutoff:
                    continue

                title = post.get("title", "")
                description = post.get("selftext", "")

                if not self._passes_keywords(title + " " + description):
                    continue

                ups = post.get("ups", 0)
                comments = post.get("num_comments", 0)
                score = self._score_trend(ups, comments)

                trends.append(
                    {
                        "timestamp": now.isoformat(),
                        "source": self.source_name,
                        "source_type": "reddit",
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
