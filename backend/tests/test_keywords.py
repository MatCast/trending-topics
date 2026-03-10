"""Tests for the keyword management API."""


def test_list_keywords(client):
    """GET /api/keywords returns all keywords for the user."""
    response = client.get("/api/keywords")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    texts = [kw["text"] for kw in data]
    assert "AI" in texts
    assert "startup" in texts
    assert "blockchain" in texts


def test_create_keywords(client):
    """POST /api/keywords creates new keywords."""
    response = client.post("/api/keywords", json={
        "keywords": ["GPT", "machine learning"]
    })
    assert response.status_code == 201

    data = response.json()
    assert len(data) == 2
    texts = [kw["text"] for kw in data]
    assert "GPT" in texts
    assert "machine learning" in texts


def test_create_keywords_with_commas_and_whitespace(client):
    """Keywords are trimmed and empty entries are filtered."""
    response = client.post("/api/keywords", json={
        "keywords": ["  deep learning  ", "", "   ", "neural nets"]
    })
    assert response.status_code == 201

    data = response.json()
    texts = [kw["text"] for kw in data]
    assert "deep learning" in texts
    assert "neural nets" in texts


def test_create_duplicate_keyword_skipped(client):
    """Duplicate keywords (case-insensitive) are silently skipped."""
    response = client.post("/api/keywords", json={
        "keywords": ["ai", "AI", "Startup"]  # 'AI' and 'startup' already exist
    })
    assert response.status_code == 201

    data = response.json()
    # All should be skipped (AI and startup already exist)
    assert len(data) == 0


def test_toggle_keyword_enabled(client):
    """PUT /api/keywords/{id} toggles the enabled flag."""
    response = client.put("/api/keywords/kw_001", json={
        "enabled": False
    })
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == "kw_001"
    assert data["enabled"] is False


def test_bulk_enable_keywords(client):
    """POST /api/keywords/bulk enables selected keywords."""
    response = client.post("/api/keywords/bulk", json={
        "keyword_ids": ["kw_003"],
        "action": "enable"
    })
    assert response.status_code == 200

    data = response.json()
    assert data["action"] == "enable"
    assert data["affected"] == 1


def test_bulk_delete_keywords(client):
    """POST /api/keywords/bulk deletes selected keywords."""
    response = client.post("/api/keywords/bulk", json={
        "keyword_ids": ["kw_003"],
        "action": "delete"
    })
    assert response.status_code == 200

    data = response.json()
    assert data["action"] == "delete"
    assert data["affected"] == 1


def test_delete_single_keyword(client):
    """DELETE /api/keywords/{id} removes a keyword."""
    response = client.delete("/api/keywords/kw_001")
    assert response.status_code == 204

    # Verify it's gone
    list_response = client.get("/api/keywords")
    ids = [kw["id"] for kw in list_response.json()]
    assert "kw_001" not in ids
