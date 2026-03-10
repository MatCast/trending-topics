"""Tests for user source CRUD operations."""


def test_create_source_with_valid_source_id(client):
    """POST /api/sources with a valid source_id succeeds."""
    response = client.post("/api/sources", json={
        "source_id": "bluesky",
        "enabled": True,
        "use_global_keywords": True,
    })
    assert response.status_code == 201

    data = response.json()
    assert data["source_id"] == "bluesky"
    assert data["enabled"] is True


def test_create_source_with_invalid_source_id(client):
    """POST /api/sources with unknown source_id returns 400."""
    response = client.post("/api/sources", json={
        "source_id": "twitter",
        "enabled": True,
    })
    assert response.status_code == 400
    assert "Unknown source_id" in response.json()["detail"]


def test_create_duplicate_singleton(client):
    """Singleton sources re-enable existing instead of creating a duplicate."""
    # hackernews already exists in MOCK_USER_SOURCES
    response = client.post("/api/sources", json={
        "source_id": "hackernews",
        "enabled": True,
    })
    assert response.status_code == 201

    data = response.json()
    assert data["source_id"] == "hackernews"
    assert data["enabled"] is True
    # Should return the existing source (id matches original)
    assert data["id"] == "src_002"


def test_create_multi_instance_allows_duplicates(client):
    """Multi-instance sources allow multiple with different params."""
    response = client.post("/api/sources", json={
        "source_id": "reddit",
        "enabled": True,
        "params": {"subreddit": "machinelearning"},
    })
    assert response.status_code == 201

    data = response.json()
    assert data["source_id"] == "reddit"
    assert data["params"]["subreddit"] == "machinelearning"
    assert data.get("existed") is not True


def test_list_user_sources(client):
    """GET /api/sources returns the user's configured sources."""
    response = client.get("/api/sources")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least the mocked sources

    # All sources should have source_id
    for source in data:
        assert "source_id" in source
        assert "id" in source


def test_toggle_source_enabled(client):
    """PUT /api/sources/{id} updates the enabled flag."""
    response = client.put("/api/sources/src_001", json={
        "enabled": False,
    })
    assert response.status_code == 200

    data = response.json()
    assert data["enabled"] is False


def test_delete_source(client):
    """DELETE /api/sources/{id} removes the source."""
    response = client.delete("/api/sources/src_001")
    assert response.status_code == 204

    # Verify it's gone
    list_response = client.get("/api/sources")
    source_ids = [s["id"] for s in list_response.json()]
    assert "src_001" not in source_ids
