"""Firebase Admin SDK client for Firestore operations."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

_app: Optional[firebase_admin.App] = None
_db = None


# --- Default Source Catalog Data ---

SOURCE_CATALOG_DEFAULTS: Dict[str, Dict[str, Any]] = {
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
            "subreddit": {
                "type": "string",
                "required": True,
                "label": "Subreddit name",
                "placeholder": "e.g., startups",
            }
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


def init_firebase(service_account_path: Optional[str] = None):
    """Initialize Firebase Admin SDK. Call once at startup."""
    global _app, _db
    if _app is not None:
        return

    if service_account_path:
        cred = credentials.Certificate(service_account_path)
        _app = firebase_admin.initialize_app(cred)
    else:
        # Uses GOOGLE_APPLICATION_CREDENTIALS env var or default credentials
        _app = firebase_admin.initialize_app()

    _db = firestore.client()
    logger.info("Firebase Admin SDK initialized.")


def get_db():
    """Get Firestore client. Raises if not initialized."""
    if _db is None:
        raise RuntimeError("Firebase not initialized. Call init_firebase() first.")
    return _db


# --- Source Catalog Operations ---


def seed_source_catalog():
    """Seed the top-level sources catalog if it doesn't exist.
    Called once at startup.
    """
    db = get_db()
    sources_ref = db.collection("sources")

    for source_id, source_data in SOURCE_CATALOG_DEFAULTS.items():
        doc_ref = sources_ref.document(source_id)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set(source_data)
            logger.info(f"Seeded catalog source: {source_id}")
        else:
            logger.debug(f"Catalog source '{source_id}' already exists, skipping seed.")


def list_catalog_sources(user_tier: str = "free") -> List[Dict[str, Any]]:
    """List all sources from the catalog, filtered by visibility.

    Visibility tiers (lowest to highest): disabled, public, beta, pro.
    - 'free' users see 'public' sources only.
    - 'beta' users see 'public' + 'beta'.
    - 'pro' users see 'public' + 'beta' + 'pro'.
    - 'disabled' sources are always hidden.
    """
    db = get_db()
    docs = db.collection("sources").stream()

    tier_access = {
        "free": {"public"},
        "beta": {"public", "beta"},
        "pro": {"public", "beta", "pro"},
        "admin": {"public", "beta", "pro"},
    }
    allowed = tier_access.get(user_tier, {"public"})

    results = []
    for doc in docs:
        data = doc.to_dict()
        visibility = data.get("visibility", "public")
        if visibility in allowed:
            results.append({"id": doc.id, **data})

    return results


def get_catalog_source(source_id: str) -> Optional[Dict[str, Any]]:
    """Get a single catalog entry by ID."""
    db = get_db()
    doc = db.collection("sources").document(source_id).get()
    if doc.exists:
        return {"id": doc.id, **doc.to_dict()}
    return None


# --- User Operations ---


def get_or_create_user(
    uid: str, email: str = "", display_name: str = ""
) -> Dict[str, Any]:
    """Get user doc, create if doesn't exist. Returns user data."""
    db = get_db()
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    if user_doc.exists:
        return user_doc.to_dict()

    user_data = {
        "uid": uid,
        "email": email,
        "display_name": display_name,
        "created_at": datetime.now(timezone.utc),
        "active_tier": "free",
        "settings": {
            "time_window_hours": 3,
            "max_trends_per_source": 3,
            "result_retention_days": 15,
            "schedule": {"type": "manual"},
        },
    }
    user_ref.set(user_data)
    logger.info(f"Created new user: {uid}")
    return user_data


def get_user_settings(uid: str) -> Dict[str, Any]:
    """Get user settings."""
    db = get_db()
    user_doc = db.collection("users").document(uid).get()
    if not user_doc.exists:
        return {}
    return user_doc.to_dict().get("settings", {})


def update_user_settings(uid: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Update user settings (partial merge)."""
    db = get_db()
    user_ref = db.collection("users").document(uid)

    # Merge into the settings map
    update_data = {f"settings.{k}": v for k, v in settings.items()}
    user_ref.update(update_data)

    return get_user_settings(uid)


# --- User Source Config Operations ---


def list_sources(uid: str) -> List[Dict[str, Any]]:
    """List all source configs for a user from user_sources sub-collection."""
    db = get_db()
    sources_ref = db.collection("users").document(uid).collection("user_sources")
    docs = sources_ref.stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def create_source(
    uid: str, source_data: Dict[str, Any], user_tier: str = "free"
) -> Dict[str, Any]:
    """Create a new user source subscription. Validates against catalog.

    Args:
        uid: Firebase user ID.
        source_data: Dict with source_id, optional name, enabled, use_global_keywords, params.
    """
    db = get_db()
    source_id = source_data.get("source_id", "")

    # Validate source_id exists in catalog
    catalog_entry = get_catalog_source(source_id)
    if not catalog_entry:
        raise ValueError(
            f"Unknown source_id: '{source_id}'. Source not found in catalog."
        )

    is_multi = catalog_entry.get("is_multi_instance", False)

    # Use catalog name if not provided
    if not source_data.get("name"):
        if is_multi and source_data.get("params", {}).get("subreddit"):
            source_data["name"] = f"r/{source_data['params']['subreddit']}"
        else:
            source_data["name"] = catalog_entry.get("name", source_id)

    # Merge default_params from catalog (user params take precedence)
    default_params = catalog_entry.get("default_params", {})
    merged_params = {**default_params, **source_data.get("params", {})}
    source_data["params"] = merged_params

    # Deduplicate and Handle Limits
    if source_id == "reddit":
        limit = get_reddit_source_limit(user_tier)
        subreddit = source_data.get("params", {}).get("subreddit", "").lower()

        if subreddit:
            # Fetch all existing reddit sources for this user
            existing_reddit_sources = list(
                db.collection("users")
                .document(uid)
                .collection("user_sources")
                .where("source_id", "==", "reddit")
                .stream()
            )

            active_count = sum(
                1 for d in existing_reddit_sources if d.to_dict().get("enabled", True)
            )

            # 1. Check for duplicates first
            for doc in existing_reddit_sources:
                doc_data = doc.to_dict()
                if doc_data.get("params", {}).get("subreddit", "").lower() == subreddit:
                    # If user is trying to re-enable it
                    if source_data.get("enabled", True) and not doc_data.get(
                        "enabled", True
                    ):
                        if limit != -1 and active_count >= limit:
                            logger.warning(
                                f"Reddit source limit reached ({limit}) for user {uid}"
                            )
                            # If they added it explicitly as enabled but are over limit, we keep it disabled
                            return {"id": doc.id, **doc_data, "existed": True}

                        doc.reference.update({"enabled": True})
                        logger.info(
                            f"Subreddit r/{subreddit} re-enabled for user {uid}"
                        )
                        return {
                            "id": doc.id,
                            **doc_data,
                            "enabled": True,
                            "existed": True,
                        }

                    return {"id": doc.id, **doc_data, "existed": True}

            # 2. Truly new subreddit. If at limit, force disabled.
            if limit != -1 and active_count >= limit:
                logger.info(
                    f"Limit reached ({limit}). Adding subreddit r/{subreddit} as disabled for {uid}"
                )
                source_data["enabled"] = False

    elif not is_multi:
        # Singleton: only one per source_id per user (e.g., hackernews, bluesky)
        existing = (
            db.collection("users")
            .document(uid)
            .collection("user_sources")
            .where("source_id", "==", source_id)
            .stream()
        )
        for doc in existing:
            # Re-enable the existing source instead of creating a duplicate
            doc.reference.update({"enabled": True})
            updated = doc.reference.get().to_dict()
            logger.info(
                f"Source '{source_id}' already exists for user {uid}, re-enabled it."
            )
            return {"id": doc.id, **updated, "existed": True}

    source_data["created_at"] = datetime.now(timezone.utc)
    sources_ref = db.collection("users").document(uid).collection("user_sources")
    doc_ref = sources_ref.add(source_data)
    # doc_ref is a tuple: (timestamp, DocumentReference)
    doc_id = doc_ref[1].id
    return {"id": doc_id, **source_data}


def update_source(
    uid: str, source_id: str, update_data: Dict[str, Any], user_tier: str = "free"
) -> Dict[str, Any]:
    """Update a user source config."""
    db = get_db()
    source_ref = (
        db.collection("users")
        .document(uid)
        .collection("user_sources")
        .document(source_id)
    )

    # Enforce Reddit Limit on Toggle
    if update_data.get("enabled") is True:
        source_doc = source_ref.get()
        if source_doc.exists:
            source_data = source_doc.to_dict()
            if source_data.get("source_id") == "reddit" and not source_data.get(
                "enabled", True
            ):
                limit = get_reddit_source_limit(user_tier)
                if limit != -1:
                    active_count = (
                        db.collection("users")
                        .document(uid)
                        .collection("user_sources")
                        .where("source_id", "==", "reddit")
                        .where("enabled", "==", True)
                        .stream()
                    )
                    # Use sum to count stream to avoid composite index if possible,
                    # but here where/where might need one. Let's stick to memory count for simplicity/safety.
                    # Or just reuse the check from create_source
                    existing_reddit_sources = list(
                        db.collection("users")
                        .document(uid)
                        .collection("user_sources")
                        .where("source_id", "==", "reddit")
                        .stream()
                    )
                    active_count = sum(
                        1
                        for d in existing_reddit_sources
                        if d.to_dict().get("enabled", True)
                    )

                    if active_count >= limit:
                        logger.warning(
                            f"Cannot enable Reddit source. Limit ({limit}) reached for user {uid}"
                        )
                        raise ValueError(
                            (f"Limit reached. Your tier allows a maximum of {limit}"
                             " active subreddits. Disable one to enable another.")
                        )

    source_ref.update(update_data)
    updated = source_ref.get()
    return {"id": source_id, **updated.to_dict()}


def delete_source(uid: str, source_id: str):
    """Delete a user source config."""
    db = get_db()
    db.collection("users").document(uid).collection("user_sources").document(
        source_id
    ).delete()


# --- Keyword Operations ---

# Default Tier Limits for reference and fallbacks
DEFAULT_KEYWORD_LIMITS = {
    "free": 20,
    "pro": 100,
    "unlimited": -1,
}

DEFAULT_REDDIT_SOURCE_LIMITS = {
    "free": 3,
    "beta": 10,
    "pro": -1,
}


def get_keyword_limit(user_tier: str = "free") -> int:
    """Get max keywords for a user tier. Returns -1 for unlimited."""
    config = get_admin_config()
    tier_limits = config.get("tier_limits", {}).get("keywords", {})
    return tier_limits.get(user_tier, DEFAULT_KEYWORD_LIMITS.get(user_tier, 20))


def get_reddit_source_limit(user_tier: str = "free") -> int:
    """Get max reddit sources for a user tier. Returns -1 for unlimited."""
    config = get_admin_config()
    tier_limits = config.get("tier_limits", {}).get("reddit_sources", {})
    return tier_limits.get(user_tier, DEFAULT_REDDIT_SOURCE_LIMITS.get(user_tier, 3))


def list_keywords(uid: str) -> List[Dict[str, Any]]:
    """List all keywords for a user."""
    db = get_db()
    docs = db.collection("users").document(uid).collection("keywords").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def list_enabled_keywords(uid: str) -> List[str]:
    """List only enabled keyword texts. Used for extraction."""
    db = get_db()
    docs = (
        db.collection("users")
        .document(uid)
        .collection("keywords")
        .where("enabled", "==", True)
        .stream()
    )
    return [doc.to_dict().get("text", "") for doc in docs if doc.to_dict().get("text")]


def create_keywords(
    uid: str, keywords: List[str], user_tier: str = "free"
) -> List[Dict[str, Any]]:
    """Create keywords in bulk. Trims, deduplicates (case-insensitive), enforces limits.

    Returns list of created keyword dicts.
    """
    db = get_db()
    keywords_ref = db.collection("users").document(uid).collection("keywords")

    # Get existing keywords for dedup
    existing_docs = list(keywords_ref.stream())
    existing_texts = {doc.to_dict().get("text", "").lower() for doc in existing_docs}
    current_count = len(existing_docs)

    # Check limit
    limit = get_keyword_limit(user_tier)

    # Process and deduplicate input
    created = []
    seen = set()
    for kw_raw in keywords:
        kw = kw_raw.strip()
        if not kw:
            continue
        kw_lower = kw.lower()
        if kw_lower in existing_texts or kw_lower in seen:
            continue

        # Check limit (-1 = unlimited)
        if limit != -1 and (current_count + len(created)) >= limit:
            logger.warning(f"Keyword limit ({limit}) reached for user {uid}")
            break

        now = datetime.now(timezone.utc)
        doc_ref = keywords_ref.document()
        keyword_data = {
            "text": kw,
            "enabled": True,
            "created_at": now,
        }
        doc_ref.set(keyword_data)
        created.append({"id": doc_ref.id, **keyword_data})
        seen.add(kw_lower)

    logger.info(f"Created {len(created)} keywords for user {uid}")
    return created


def update_keyword(
    uid: str, keyword_id: str, update_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update a single keyword (e.g., toggle enabled)."""
    db = get_db()
    kw_ref = (
        db.collection("users").document(uid).collection("keywords").document(keyword_id)
    )
    kw_ref.update(update_data)
    updated = kw_ref.get()
    return {"id": keyword_id, **updated.to_dict()}


def bulk_update_keywords(
    uid: str, keyword_ids: List[str], update_data: Dict[str, Any]
) -> int:
    """Bulk update keywords (e.g., enable/disable multiple)."""
    db = get_db()
    batch = db.batch()
    count = 0
    keywords_ref = db.collection("users").document(uid).collection("keywords")

    for kid in keyword_ids:
        batch.update(keywords_ref.document(kid), update_data)
        count += 1
        if count >= 400:
            batch.commit()
            batch = db.batch()

    if count % 400 != 0:
        batch.commit()

    return count


def delete_keywords(uid: str, keyword_ids: List[str]) -> int:
    """Bulk delete keywords."""
    db = get_db()
    batch = db.batch()
    count = 0
    keywords_ref = db.collection("users").document(uid).collection("keywords")

    for kid in keyword_ids:
        batch.delete(keywords_ref.document(kid))
        count += 1
        if count >= 400:
            batch.commit()
            batch = db.batch()

    if count % 400 != 0:
        batch.commit()

    logger.info(f"Deleted {count} keywords for user {uid}")
    return count


def delete_keyword(uid: str, keyword_id: str):
    """Delete a single keyword."""
    db = get_db()
    db.collection("users").document(uid).collection("keywords").document(
        keyword_id
    ).delete()


# --- Results Operations ---


def create_pending_extraction(uid: str, sources_used: List[str]) -> str:
    """Create an extraction document with status 'pending' and return its ID."""
    db = get_db()
    now = datetime.now(timezone.utc)
    extraction_ref = (
        db.collection("users").document(uid).collection("extractions").document()
    )
    extraction_id = extraction_ref.id

    extraction_data = {
        "id": extraction_id,
        "created_at": now,
        "status": "pending",
        "sources": sources_used,
        "results_count": 0,
    }
    extraction_ref.set(extraction_data)
    logger.info(f"Created pending extraction {extraction_id} for user {uid}")
    return extraction_id


def update_extraction_status(
    uid: str, extraction_id: str, status: str, error: str = None
):
    """Update the status of an existing extraction document."""
    db = get_db()
    extraction_ref = (
        db.collection("users")
        .document(uid)
        .collection("extractions")
        .document(extraction_id)
    )

    update_data = {"status": status}
    if error:
        update_data["error"] = error

    extraction_ref.update(update_data)
    logger.info(f"Updated extraction {extraction_id} status to {status} for user {uid}")


def store_results(
    uid: str,
    extraction_id: str,
    results: List[Dict[str, Any]],
    sources_used: List[str],
    retention_days: int = 15,
):
    """Update extraction run metadata and store its results in Firestore with TTL."""
    db = get_db()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=retention_days)
    batch = db.batch()

    # 1. Update the existing Extraction document
    extraction_ref = (
        db.collection("users")
        .document(uid)
        .collection("extractions")
        .document(extraction_id)
    )
    extraction_data = {
        "status": "completed",
        "expires_at": expires_at,
        "results_count": len(results),
        "sources": sources_used,
    }
    batch.update(extraction_ref, extraction_data)

    # 2. Store individual results
    results_ref = db.collection("users").document(uid).collection("results")

    for result in results:
        doc_ref = results_ref.document()

        # Update the result dict in-place so it's returned to the caller with its new fields
        result["id"] = doc_ref.id
        result["extraction_id"] = extraction_id
        result["created_at"] = now
        result["expires_at"] = expires_at

        batch.set(doc_ref, result)

    batch.commit()
    logger.info(
        f"Stored extraction {extraction_id} with {len(results)} results for user {uid}"
    )


def list_extractions(
    uid: str,
    page: int = 1,
    page_size: int = 50,
) -> tuple[List[Dict[str, Any]], int]:
    """List extraction history for a user with pagination."""
    db = get_db()
    query = db.collection("users").document(uid).collection("extractions")

    # Sort
    query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

    # Filter expired extractions in memory
    now = datetime.now(timezone.utc)
    all_docs = list(query.stream())

    filtered_docs = []
    for doc in all_docs:
        data = doc.to_dict()
        if data.get("expires_at", now + timedelta(days=1)) <= now:
            continue
        filtered_docs.append(doc)

    total = len(filtered_docs)

    start = (page - 1) * page_size
    end = start + page_size
    page_docs = filtered_docs[start:end]

    results = [{"id": doc.id, **doc.to_dict()} for doc in page_docs]
    return results, total


def list_results(
    uid: str,
    extraction_id: Optional[str] = None,
    source_type: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 50,
) -> tuple[List[Dict[str, Any]], int]:
    """List results for a user, optionally filtered by extraction_id or source_type."""
    db = get_db()

    # Base query
    query = db.collection("users").document(uid).collection("results")

    # If using extraction_id, query specifically for it to save reads
    if extraction_id:
        query = query.where("extraction_id", "==", extraction_id)

    if source_type:
        query = query.where("source_type", "==", source_type)

    # Note: FireStore requires a composite index if combining where() and order_by().
    # For now, we will fetch and sort in memory if extraction_id or source_type is used.

    if not extraction_id and not source_type:
        direction = (
            firestore.Query.DESCENDING
            if sort_order == "desc"
            else firestore.Query.ASCENDING
        )
        query = query.order_by(sort_by, direction=direction)

    all_docs = list(query.stream())
    now = datetime.now(timezone.utc)

    # Filter in memory for expired out of safety
    filtered_docs = []
    for doc in all_docs:
        data = doc.to_dict()
        if data.get("expires_at", now + timedelta(days=1)) <= now:
            continue
        filtered_docs.append(data)

    # Sort in memory if extraction_id is used since we skipped order_by to avoid composite index requirement
    if extraction_id:
        reverse = sort_order == "desc"
        # Safely sort using get
        filtered_docs.sort(
            key=lambda x: x.get(sort_by) if x.get(sort_by) is not None else "",
            reverse=reverse,
        )

    total = len(filtered_docs)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_docs = filtered_docs[start:end]

    results = [{"id": doc.get("id"), **doc} for doc in page_docs]
    return results, total


def get_all_results_for_export(
    uid: str, extraction_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all non-expired results for CSV export, optionally filtered by extraction_id."""
    db = get_db()

    query = db.collection("users").document(uid).collection("results")

    if extraction_id:
        query = query.where("extraction_id", "==", extraction_id)
    else:
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

    now = datetime.now(timezone.utc)
    docs = query.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        if data.get("expires_at", now + timedelta(days=1)) > now:
            results.append({"id": doc.id, **data})

    return results


def delete_result(uid: str, result_id: str):
    """Delete a single result."""
    db = get_db()
    db.collection("users").document(uid).collection("results").document(
        result_id
    ).delete()


# --- Cleanup Operations ---


def cleanup_expired_results():
    """Delete all expired results and extractions across all users. Called by scheduled job."""
    db = get_db()
    now = datetime.now(timezone.utc)
    deleted_count = 0

    users = db.collection("users").stream()
    for user_doc in users:
        # 1. Clean up Results
        results_query = user_doc.reference.collection("results").where(
            "expires_at", "<=", now
        )
        expired_docs = results_query.stream()
        batch = db.batch()
        batch_count = 0
        for doc in expired_docs:
            batch.delete(doc.reference)
            batch_count += 1
            deleted_count += 1

            if batch_count >= 400:
                batch.commit()
                batch = db.batch()
                batch_count = 0

        if batch_count > 0:
            batch.commit()

        # 2. Clean up Extractions
        extractions_query = user_doc.reference.collection("extractions").where(
            "expires_at", "<=", now
        )
        expired_extractions = extractions_query.stream()

        batch = db.batch()
        batch_count = 0
        for doc in expired_extractions:
            batch.delete(doc.reference)
            batch_count += 1
            deleted_count += 1

            if batch_count >= 400:
                batch.commit()
                batch = db.batch()
                batch_count = 0

        if batch_count > 0:
            batch.commit()

    logger.info(
        f"Cleaned up {deleted_count} expired documents (results + extractions)."
    )
    return deleted_count


# --- Admin Config ---


def get_admin_config() -> Dict[str, Any]:
    """Get global admin configuration."""
    db = get_db()
    doc = db.collection("admin").document("config").get()
    if doc.exists:
        return doc.to_dict()
    # Return defaults
    defaults = {
        "source_weights": {
            "reddit": 1.0,
            "hackernews": 1.0,
            "bluesky": 1.0,
            "indiehackers": 1.0,
        },
        "default_retention_days": 15,
        "tier_limits": {
            "keywords": DEFAULT_KEYWORD_LIMITS,
            "reddit_sources": DEFAULT_REDDIT_SOURCE_LIMITS,
        },
    }
    db.collection("admin").document("config").set(defaults)
    return defaults


def update_admin_config(update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update global admin configuration."""
    db = get_db()
    doc_ref = db.collection("admin").document("config")
    doc_ref.set(update_data, merge=True)
    return doc_ref.get().to_dict()


# --- Schedule helpers ---


def get_users_with_active_schedules() -> List[Dict[str, Any]]:
    """Get all users who have a non-manual schedule configured."""
    db = get_db()
    users = db.collection("users").stream()
    active = []
    for user_doc in users:
        data = user_doc.to_dict()
        settings = data.get("settings", {})
        schedule = settings.get("schedule", {})
        if schedule.get("type", "manual") != "manual":
            active.append({"uid": user_doc.id, **data})
    return active
