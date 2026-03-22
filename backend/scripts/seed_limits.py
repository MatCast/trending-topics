import os
import sys

# Add the backend directory to sys.path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.firebase_client import init_firebase, get_db, DEFAULT_EXTRACTION_LIMITS

    print("Successfully imported firebase_client.")
except ImportError as e:
    print(
        "Error: Could not import app modules."
        f"Make sure you are running this from the backend directory. Detail: {e}"
    )
    sys.exit(1)


def seed_extraction_limits():
    """Update the Firestore admin/config document with the current DEFAULT_EXTRACTION_LIMITS."""
    print("Initializing Firebase...")
    init_firebase()
    db = get_db()

    config_ref = db.collection("admin").document("config")

    print(f"Updating extraction limits to: {DEFAULT_EXTRACTION_LIMITS}")

    # Use merge=True to avoid overwriting other config fields like source_weights
    config_ref.set(
        {"tier_limits": {"extractions": DEFAULT_EXTRACTION_LIMITS}}, merge=True
    )

    print("Successfully updated admin/config in Firestore.")


if __name__ == "__main__":
    seed_extraction_limits()
