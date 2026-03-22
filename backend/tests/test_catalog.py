"""Tests for the source catalog API."""

from tests.conftest import MOCK_CATALOG


def test_list_catalog_returns_all_sources(client):
    """GET /api/sources/catalog returns all public sources."""
    response = client.get("/api/sources/catalog")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4

    source_ids = [s["id"] for s in data]
    assert "reddit" in source_ids
    assert "hackernews" in source_ids
    assert "bluesky" in source_ids
    assert "indiehackers" in source_ids


def test_catalog_contains_required_fields(client):
    """Each catalog entry has all required metadata fields."""
    response = client.get("/api/sources/catalog")
    assert response.status_code == 200

    required_fields = [
        "id",
        "name",
        "description",
        "icon",
        "visibility",
        "config_schema",
        "is_multi_instance",
    ]

    for source in response.json():
        for field in required_fields:
            assert (
                field in source
            ), f"Missing field '{field}' in source '{source.get('id')}'"


def test_catalog_filters_by_visibility(client, mock_firebase):
    """Disabled sources are excluded from catalog results."""
    # Temporarily change bluesky visibility to disabled
    original = MOCK_CATALOG["bluesky"]["visibility"]
    MOCK_CATALOG["bluesky"]["visibility"] = "disabled"

    try:
        response = client.get("/api/sources/catalog")
        assert response.status_code == 200

        source_ids = [s["id"] for s in response.json()]
        assert "bluesky" not in source_ids
        # Other sources should still be present
        assert "reddit" in source_ids
        assert "hackernews" in source_ids
    finally:
        # Restore original
        MOCK_CATALOG["bluesky"]["visibility"] = original
