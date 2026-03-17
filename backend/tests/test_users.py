"""Tests for the users router."""

def test_get_my_profile(client, mock_firebase):
    """GET /api/users/me returns valid user profile and tier limits."""
    response = client.get("/api/users/me")
    assert response.status_code == 200
    
    data = response.json()
    assert data["uid"] == "test_user_123"
    assert "active_tier" in data
    assert "tier_limits" in data
    assert "keywords" in data["tier_limits"]
    assert "reddit_sources" in data["tier_limits"]
    assert "settings" in data
