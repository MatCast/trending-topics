"""Base parser class and factory function."""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TrendParser:
    """Base class for all source parsers."""

    def __init__(
        self,
        source_name: str,
        time_window_hours: int,
        keywords: List[str],
        weight: float = 1.0,
        params: Dict[str, Any] = None,
    ):
        self.source_name = source_name
        self.time_window_hours = time_window_hours
        self.keywords = [k.lower() for k in keywords]
        self.weight = weight
        self.params = params or {}

    def fetch(self) -> List[Dict[str, Any]]:
        """Must be implemented by subclasses. Returns a list of standardized trend dicts."""
        raise NotImplementedError

    def _score_trend(self, ups: int, comments: int) -> float:
        return (ups + (comments * 2)) * self.weight

    def _passes_keywords(self, text: str) -> bool:
        if not self.keywords:
            return True
        text_lower = text.lower()
        return any(k in text_lower for k in self.keywords)


def get_parser(
    source_type: str,
    source_name: str,
    time_window_hours: int,
    keywords: List[str],
    weight: float = 1.0,
    params: Dict[str, Any] = None,
) -> TrendParser:
    """Factory function to create the correct parser for a source type."""
    from .reddit import RedditParser
    from .hackernews import HackerNewsParser
    from .bluesky import BlueskyParser

    source_type = source_type.lower()
    if source_type == "reddit":
        return RedditParser(source_name, time_window_hours, keywords, weight, params)
    elif source_type == "hackernews":
        return HackerNewsParser(source_name, time_window_hours, keywords, weight, params)
    elif source_type == "bluesky":
        return BlueskyParser(source_name, time_window_hours, keywords, weight, params)
    else:
        raise ValueError(f"Unknown source type: '{source_type}'")
