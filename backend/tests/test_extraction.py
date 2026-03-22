"""Tests for the extraction endpoint with catalog-linked sources."""

from unittest.mock import patch


def test_extraction_with_catalog_sources(client, mock_firebase):
    """POST /api/extract works with source_id-linked sources."""
    # Patch at the router level where run_extraction is imported
    with patch("app.routers.extraction.run_extraction") as mock_run:
        mock_run.return_value = {
            "extraction_id": "test-run-001",
            "status": "completed",
            "results_count": 2,
            "results": [
                {
                    "id": "r1",
                    "source": "r/startups",
                    "source_type": "reddit",
                    "title": "Test Trend 1",
                    "url": "https://example.com/1",
                    "trend_score": 42.0,
                    "ups": 20,
                    "comments": 5,
                },
                {
                    "id": "r2",
                    "source": "Hacker News",
                    "source_type": "hackernews",
                    "title": "Test Trend 2",
                    "url": "https://example.com/2",
                    "trend_score": 38.0,
                    "ups": 15,
                    "comments": 3,
                },
            ],
        }

        response = client.post("/api/extract", json={})
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "pending"
        assert data["results_count"] == 0
        assert len(data["results"]) == 0

        # Verify run_extraction was called with source_id-based sources
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs
        sources_arg = call_kwargs.get("sources", [])
        for src in sources_arg:
            assert "source_id" in src


def test_extraction_skips_disabled_sources(client, mock_firebase):
    """Disabled sources are passed to run_extraction (it handles filtering
    internally).
    """
    with patch("app.routers.extraction.run_extraction") as mock_run:
        mock_run.return_value = None  # It's a background task now

        response = client.post("/api/extract", json={})
        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        mock_run.assert_called_once()


def test_extraction_no_sources_returns_400(client, mock_firebase):
    """POST /api/extract with no sources returns 400."""
    # Override list_sources to return empty
    with patch.object(mock_firebase, "list_sources", return_value=[]):
        response = client.post("/api/extract", json={})
        assert response.status_code == 400
        assert "No sources configured" in response.json()["detail"]


def test_extraction_concurrency_limit(client, mock_firebase):
    """POST /api/extract returns 400 if an extraction is already active."""
    with patch("app.routers.extraction.fb.has_active_extraction", return_value=True):
        response = client.post("/api/extract", json={})
        assert response.status_code == 400
        assert "extraction in progress" in response.json()["detail"].lower()


def test_extraction_quota_limit(client, mock_firebase):
    """POST /api/extract returns 429 if volume quota is exceeded."""
    with patch(
        "app.routers.extraction.fb.check_and_increment_extraction_quota",
        return_value=(False, "daily"),
    ):
        response = client.post("/api/extract", json={})
        assert response.status_code == 429
        assert "daily extraction limit" in response.json()["detail"].lower()
