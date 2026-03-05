import json
import logging
from datetime import datetime, timedelta, timezone
import time
from typing import List, Dict, Any
import re
import os

logger = logging.getLogger(__name__)


class TrendResearcher:
    def __init__(
        self, sources_file: str, sheets_manager=None, time_window_hours: int = None
    ):
        self.sources_file = sources_file
        self.sheets_manager = sheets_manager

        if time_window_hours is None:
            time_window_hours = int(os.environ.get("TIME_WINDOW_HOURS", 3))

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
            r"<(script|style).*?>.*?</\1>",
            "",
            html_content,
            flags=re.DOTALL | re.IGNORECASE,
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

    def fetch_trends(
        self, max_trends: int = None, use_keywords: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetches trends using source-specific parsers.
        Returns the top N trending topics PER source type.
        """
        import sys

        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from parsers import get_parser

        config = self._load_sources()
        sources_list = config.get("sources", [])
        filters = config.get("filters", {})

        keywords = []
        if use_keywords:
            keywords = filters.get("keywords", [])

        if max_trends is None:
            max_trends = int(os.environ.get("MAX_TOP_TRENDS", 3))

        source_trends = {}  # Grouped by source name

        # 1. Fetch Trends via Parsers
        for source_config in sources_list:
            source_name = source_config.get("name", "Unknown Source")
            try:
                # Instantiate the appropriate parser
                parser = get_parser(
                    source_config=source_config,
                    time_window_hours=self.time_window_hours,
                    keywords=keywords,
                )

                # Fetch trends for this source
                trends = parser.fetch()

                # Use the resolved source name (e.g., if it was dynamically generated)
                resolved_name = parser.source_name

                if resolved_name not in source_trends:
                    source_trends[resolved_name] = []

                source_trends[resolved_name].extend(trends)

            except Exception as e:
                logger.error(f"Failed to fetch {source_name}: {e}")

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
