"""Shared test fixtures for the backend test suite.

Mocks firebase_admin at the sys.modules level so the app can import
without the actual Firebase SDK installed.
"""

import sys
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from contextlib import ExitStack

import pytest

# --- Mock firebase_admin BEFORE any app imports ---
# This must happen before importing the FastAPI app since auth.py and
# firebase_client.py both import from firebase_admin at module level.

mock_firebase_admin = MagicMock()
mock_firebase_admin.auth = MagicMock()
mock_firebase_admin.credentials = MagicMock()
mock_firebase_admin.firestore = MagicMock()
sys.modules["firebase_admin"] = mock_firebase_admin
sys.modules["firebase_admin.auth"] = mock_firebase_admin.auth
sys.modules["firebase_admin.credentials"] = mock_firebase_admin.credentials
sys.modules["firebase_admin.firestore"] = mock_firebase_admin.firestore

# Now we can safely import the app (noqa: E402 intentional for mocking)
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.auth import verify_firebase_token  # noqa: E402


# --- Mock Firestore Data ---

MOCK_CATALOG = {
    "reddit": {
        "name": "Reddit",
        "description": "Monitor subreddits for rising posts",
        "icon": "reddit",
        "website_url": "https://reddit.com",
        "category": "social",
        "supports_keywords": True,
        "is_multi_instance": True,
        "visibility": "public",
        "config_schema": {
            "subreddit": {"type": "string", "required": True, "label": "Subreddit name"}
        },
        "default_params": {},
    },
    "hackernews": {
        "name": "Hacker News",
        "description": "Top stories filtered by your keywords",
        "icon": "hackernews",
        "website_url": "https://news.ycombinator.com",
        "category": "tech",
        "supports_keywords": True,
        "is_multi_instance": False,
        "visibility": "public",
        "config_schema": {},
        "default_params": {"url": "https://hnrss.org/newest?points=10"},
    },
    "bluesky": {
        "name": "Bluesky",
        "description": "Search posts using your global keywords",
        "icon": "bluesky",
        "website_url": "https://bsky.app",
        "category": "social",
        "supports_keywords": True,
        "is_multi_instance": False,
        "visibility": "public",
        "config_schema": {},
        "default_params": {},
    },
    "indiehackers": {
        "name": "Indie Hackers",
        "description": "Top stories from Indie Hackers RSS feed",
        "icon": "indiehackers",
        "website_url": "https://indiehackers.com",
        "category": "entrepreneurship",
        "supports_keywords": True,
        "is_multi_instance": False,
        "visibility": "public",
        "config_schema": {},
        "default_params": {},
    },
}


def _make_user_sources():
    """Create a fresh copy of mock user sources."""
    return [
        {
            "id": "src_001",
            "source_id": "reddit",
            "name": "r/startups",
            "enabled": True,
            "use_global_keywords": False,
            "params": {"subreddit": "startups"},
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        },
        {
            "id": "src_002",
            "source_id": "hackernews",
            "name": "Hacker News",
            "enabled": True,
            "use_global_keywords": True,
            "params": {"url": "https://hnrss.org/newest?points=10"},
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        },
    ]


def _mock_verify_token():
    """Mock Firebase token verification."""
    return {"uid": "test_user_123", "email": "test@example.com", "name": "Test User"}


@pytest.fixture(autouse=True)
def mock_firebase():
    """Patch firebase_client functions with in-memory mocks."""
    import app.firebase_client as fb_module

    user_sources = _make_user_sources()
    user_keywords = [
        {
            "id": "kw_001",
            "text": "AI",
            "enabled": True,
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        },
        {
            "id": "kw_002",
            "text": "startup",
            "enabled": True,
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        },
        {
            "id": "kw_003",
            "text": "blockchain",
            "enabled": False,
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        },
    ]

    # Catalog functions
    def mock_list_catalog(user_tier="free"):
        tier_access = {
            "free": {"public"},
            "beta": {"public", "beta"},
            "pro": {"public", "beta", "pro"},
        }
        allowed = tier_access.get(user_tier, {"public"})
        return [
            {"id": sid, **sdata}
            for sid, sdata in MOCK_CATALOG.items()
            if sdata.get("visibility", "public") in allowed
        ]

    def mock_get_catalog(source_id):
        data = MOCK_CATALOG.get(source_id)
        if data:
            return {"id": source_id, **data}
        return None

    def mock_list_sources(uid):
        return list(user_sources)

    def mock_create_source(uid, source_data, user_tier="free"):
        source_id = source_data.get("source_id", "")
        catalog_entry = mock_get_catalog(source_id)
        if not catalog_entry:
            raise ValueError(f"Unknown source_id: '{source_id}'")

        # Reddit Limit check (Mocked logic)
        if source_id == "reddit":
            limit = 3 if user_tier == "free" else 10
            subreddit = source_data.get("params", {}).get("subreddit", "").lower()

            # Fetch active count
            active_reddit = [
                s
                for s in user_sources
                if s.get("source_id") == "reddit" and s.get("enabled", True)
            ]
            active_count = len(active_reddit)

            # Check duplicate
            for src in user_sources:
                existing_sub = src.get("params", {}).get("subreddit", "").lower()
                if src.get("source_id") == "reddit" and existing_sub == subreddit:
                    # If trying to re-enable
                    if source_data.get("enabled", True) and not src.get(
                        "enabled", True
                    ):
                        if active_count >= limit:
                            return {**src, "existed": True}
                        src["enabled"] = True
                        return {**src, "existed": True}
                    return {**src, "existed": True}

            # It's new. If at limit, force disabled.
            if active_count >= limit:
                source_data["enabled"] = False

        is_multi = catalog_entry.get("is_multi_instance", False)
        if not is_multi:
            for existing in user_sources:
                if existing["source_id"] == source_id:
                    existing["enabled"] = True
                    return {**existing, "existed": True}

        new_id = f"src_{len(user_sources) + 1:03d}"
        new_source = {
            "id": new_id,
            **source_data,
            "created_at": datetime.now(timezone.utc),
            "enabled": source_data.get("enabled", True),
        }
        if not new_source.get("name"):
            new_source["name"] = catalog_entry.get("name", source_id)
        user_sources.append(new_source)
        return new_source

    def mock_update_source(uid, source_id, update_data, user_tier="free"):
        # Enforce Reddit Limit on Toggle in mock
        if update_data.get("enabled") is True:
            limit = 3 if user_tier == "free" else 10
            active_reddit = [
                s
                for s in user_sources
                if s.get("source_id") == "reddit" and s.get("enabled", True)
            ]

            # Find the source being updated
            for src in user_sources:
                if src["id"] == source_id:
                    if src.get("source_id") == "reddit" and not src.get(
                        "enabled", True
                    ):
                        if len(active_reddit) >= limit:
                            msg = f"Limit reached. Your tier allows a maximum of {limit} active subreddits."
                            raise ValueError(msg)
                    src.update(update_data)
                    return src
        else:
            for src in user_sources:
                if src["id"] == source_id:
                    src.update(update_data)
                    return src
        raise Exception(f"Source {source_id} not found")

    def mock_delete_source(uid, source_id):
        user_sources[:] = [s for s in user_sources if s["id"] != source_id]

    # Keyword functions
    def mock_list_keywords(uid):
        return list(user_keywords)

    def mock_list_enabled_keywords(uid):
        return [kw["text"] for kw in user_keywords if kw.get("enabled")]

    def mock_create_keywords(uid, keywords, user_tier="free"):
        existing_texts = {kw["text"].lower() for kw in user_keywords}
        created = []
        seen = set()
        for kw_raw in keywords:
            kw = kw_raw.strip()
            if not kw:
                continue
            kw_lower = kw.lower()
            if kw_lower in existing_texts or kw_lower in seen:
                continue
            new_id = f"kw_{len(user_keywords) + len(created) + 1:03d}"
            keyword_data = {
                "id": new_id,
                "text": kw,
                "enabled": True,
                "created_at": datetime.now(timezone.utc),
            }
            user_keywords.append(keyword_data)
            created.append(keyword_data)
            seen.add(kw_lower)
        return created

    def mock_update_keyword(uid, keyword_id, update_data):
        for kw in user_keywords:
            if kw["id"] == keyword_id:
                kw.update(update_data)
                return kw
        raise Exception(f"Keyword {keyword_id} not found")

    def mock_bulk_update_keywords(uid, keyword_ids, update_data):
        count = 0
        for kw in user_keywords:
            if kw["id"] in keyword_ids:
                kw.update(update_data)
                count += 1
        return count

    def mock_delete_keywords(uid, keyword_ids):
        count = 0
        for kid in keyword_ids:
            for i, kw in enumerate(user_keywords):
                if kw["id"] == kid:
                    user_keywords.pop(i)
                    count += 1
                    break
        return count

    def mock_delete_keyword(uid, keyword_id):
        for i, kw in enumerate(user_keywords):
            if kw["id"] == keyword_id:
                user_keywords.pop(i)
                return

    # Patch the module-level functions
    with ExitStack() as stack:
        stack.enter_context(
            patch.object(
                fb_module, "list_catalog_sources", side_effect=mock_list_catalog
            )
        )
        stack.enter_context(
            patch.object(fb_module, "get_catalog_source", side_effect=mock_get_catalog)
        )
        stack.enter_context(
            patch.object(fb_module, "list_sources", side_effect=mock_list_sources)
        )
        stack.enter_context(
            patch.object(fb_module, "create_source", side_effect=mock_create_source)
        )
        stack.enter_context(
            patch.object(fb_module, "update_source", side_effect=mock_update_source)
        )
        stack.enter_context(
            patch.object(fb_module, "delete_source", side_effect=mock_delete_source)
        )
        stack.enter_context(
            patch.object(fb_module, "list_keywords", side_effect=mock_list_keywords)
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "list_enabled_keywords",
                side_effect=mock_list_enabled_keywords,
            )
        )
        stack.enter_context(
            patch.object(fb_module, "create_keywords", side_effect=mock_create_keywords)
        )
        stack.enter_context(
            patch.object(fb_module, "update_keyword", side_effect=mock_update_keyword)
        )
        stack.enter_context(
            patch.object(
                fb_module, "bulk_update_keywords", side_effect=mock_bulk_update_keywords
            )
        )
        stack.enter_context(
            patch.object(fb_module, "delete_keywords", side_effect=mock_delete_keywords)
        )
        stack.enter_context(
            patch.object(fb_module, "delete_keyword", side_effect=mock_delete_keyword)
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "get_or_create_user",
                return_value={"uid": "test_user_123", "active_tier": "free"},
            )
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "get_user_settings",
                return_value={
                    "time_window_hours": 3,
                    "max_trends_per_source": 3,
                },
            )
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "get_admin_config",
                return_value={
                    "source_weights": {"reddit": 1.0, "hackernews": 1.0},
                    "default_retention_days": 15,
                    "tier_limits": {
                        "keywords": {"free": 20, "pro": 100, "unlimited": -1},
                        "reddit_sources": {"free": 3, "beta": 10, "pro": -1},
                        "extractions": {
                            "free": {"daily": 1, "weekly": 2, "monthly": 3},
                            "pro": {"daily": 10, "weekly": 50, "monthly": 200},
                        },
                    },
                },
            )
        )
        stack.enter_context(
            patch.object(fb_module, "has_active_extraction", return_value=False)
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "check_and_increment_extraction_quota",
                return_value=(True, None),
            )
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "get_extraction_limits",
                return_value={"daily": 1, "weekly": 2, "monthly": 3},
            )
        )
        stack.enter_context(
            patch.object(
                fb_module,
                "get_user_extraction_usage",
                return_value={"daily": 0, "weekly": 0, "monthly": 0},
            )
        )
        stack.enter_context(patch.object(fb_module, "store_results", return_value=None))
        stack.enter_context(
            patch.object(
                fb_module, "create_pending_extraction", return_value="test-run-001"
            )
        )
        stack.enter_context(
            patch.object(fb_module, "update_extraction_status", return_value=None)
        )
        stack.enter_context(
            patch.object(fb_module, "seed_source_catalog", return_value=None)
        )
        stack.enter_context(patch.object(fb_module, "init_firebase", return_value=None))

        yield fb_module


@pytest.fixture
def client(mock_firebase):
    """FastAPI TestClient with mocked Firebase."""
    # Override the auth dependency
    app.dependency_overrides[verify_firebase_token] = _mock_verify_token

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
