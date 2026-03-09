"""Firebase Admin SDK client for Firestore operations."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from uuid import uuid4

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

_app: Optional[firebase_admin.App] = None
_db = None


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


# --- User Operations ---

def get_or_create_user(uid: str, email: str = "", display_name: str = "") -> Dict[str, Any]:
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
        "settings": {
            "global_keywords": [],
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


# --- Source Config Operations ---

def list_sources(uid: str) -> List[Dict[str, Any]]:
    """List all source configs for a user."""
    db = get_db()
    sources_ref = db.collection("users").document(uid).collection("sources")
    docs = sources_ref.stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def create_source(uid: str, source_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new source config. Prevents duplicates for reddit subreddits."""
    db = get_db()

    # Check for duplicate Reddit source
    if source_data.get("type") == "reddit":
        subreddit = source_data.get("params", {}).get("subreddit", "").lower()
        if subreddit:
            existing = (
                db.collection("users").document(uid).collection("sources")
                .where("type", "==", "reddit")
                .stream()
            )
            for doc in existing:
                if doc.to_dict().get("params", {}).get("subreddit", "").lower() == subreddit:
                    logger.warning(f"Subreddit r/{subreddit} already exists for user {uid}")
                    return {"id": doc.id, **doc.to_dict(), "existed": True}

    source_data["created_at"] = datetime.now(timezone.utc)
    sources_ref = db.collection("users").document(uid).collection("sources")
    doc_ref = sources_ref.add(source_data)
    # doc_ref is a tuple: (timestamp, DocumentReference)
    doc_id = doc_ref[1].id
    return {"id": doc_id, **source_data}


def update_source(uid: str, source_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a source config."""
    db = get_db()
    source_ref = db.collection("users").document(uid).collection("sources").document(source_id)
    source_ref.update(update_data)
    updated = source_ref.get()
    return {"id": source_id, **updated.to_dict()}


def delete_source(uid: str, source_id: str):
    """Delete a source config."""
    db = get_db()
    db.collection("users").document(uid).collection("sources").document(source_id).delete()


# --- Results Operations ---

def store_results(uid: str, run_id: str, results: List[Dict[str, Any]], retention_days: int = 15):
    """Store extraction results in Firestore with TTL."""
    db = get_db()
    expires_at = datetime.now(timezone.utc) + timedelta(days=retention_days)
    batch = db.batch()

    results_ref = db.collection("users").document(uid).collection("results")

    for result in results:
        doc_ref = results_ref.document()
        now = datetime.now(timezone.utc)

        # Update the result dict in-place so it's returned to the caller with its new fields
        result["id"] = doc_ref.id
        result["run_id"] = run_id
        result["created_at"] = now
        result["expires_at"] = expires_at

        batch.set(doc_ref, result)

    batch.commit()
    logger.info(f"Stored {len(results)} results for user {uid}, run {run_id}")


def list_results(
    uid: str,
    source_type: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 50,
) -> tuple[List[Dict[str, Any]], int]:
    """List results for a user with optional filtering and pagination."""
    db = get_db()
    query = db.collection("users").document(uid).collection("results")

    # Filter by source type
    if source_type:
        query = query.where("source_type", "==", source_type)

    # Sort
    direction = firestore.Query.DESCENDING if sort_order == "desc" else firestore.Query.ASCENDING
    query = query.order_by(sort_by, direction=direction)

    # Filtering for expired results in memory to avoid needing complex composite indexes
    # for every possible sort_by field.
    now = datetime.now(timezone.utc)

    # Get total count
    all_docs = list(query.stream())

    # Filter in memory
    filtered_docs = [
        doc for doc in all_docs
        if doc.to_dict().get("expires_at", now + timedelta(days=1)) > now
    ]
    total = len(filtered_docs)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_docs = filtered_docs[start:end]

    results = [{"id": doc.id, **doc.to_dict()} for doc in page_docs]
    return results, total


def get_all_results_for_export(uid: str) -> List[Dict[str, Any]]:
    """Get all non-expired results for CSV export."""
    db = get_db()

    query = (
        db.collection("users").document(uid).collection("results")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
    )

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
    db.collection("users").document(uid).collection("results").document(result_id).delete()


# --- Cleanup Operations ---

def cleanup_expired_results():
    """Delete all expired results across all users. Called by scheduled job."""
    db = get_db()
    now = datetime.now(timezone.utc)
    deleted_count = 0

    users = db.collection("users").stream()
    for user_doc in users:
        results_query = (
            user_doc.reference.collection("results")
            .where("expires_at", "<=", now)
        )
        expired_docs = results_query.stream()

        batch = db.batch()
        batch_count = 0
        for doc in expired_docs:
            batch.delete(doc.reference)
            batch_count += 1
            deleted_count += 1

            # Firestore batches have a 500 limit
            if batch_count >= 400:
                batch.commit()
                batch = db.batch()
                batch_count = 0

        if batch_count > 0:
            batch.commit()

    logger.info(f"Cleaned up {deleted_count} expired results.")
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
        "source_weights": {"reddit": 1.0, "hackernews": 1.0, "bluesky": 1.0},
        "default_retention_days": 15,
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
