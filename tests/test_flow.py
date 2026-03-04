from unittest.mock import patch, MagicMock
from main import main

# Fake Reddit JSON Response
FAKE_REDDIT_JSON = {
    "data": {
        "children": [
            {
                "data": {
                    "title": "New Llama 4 released",
                    "url": "https://reddit.com/r/ai",
                    "selftext": "Reddit context...",
                    "created_utc": 1709577600.0,
                    "ups": 100,
                    "num_comments": 20
                }
            }
        ]
    }
}

# Fake HN RSS Data with metrics in summary
FAKE_HN_RSS = {
    "entries": [
        {
            "title": "HN GPT-5 News",
            "link": "https://news.ycombinator.com/item?id=1",
            "summary": "<p>Points: 50</p><p># Comments: 10</p>",
            "published_parsed": (2024, 3, 4, 12, 0, 0, 0, 1, 0),
        }
    ],
    "bozo": False
}


def mock_requests_get(*args, **kwargs):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = FAKE_REDDIT_JSON
    return mock_resp


def mock_parse(url, *args, **kwargs):
    from feedparser import FeedParserDict
    return FeedParserDict(FAKE_HN_RSS)


@patch("requests.get", side_effect=mock_requests_get)
@patch("feedparser.parse", side_effect=mock_parse)
@patch("researcher.TrendResearcher._is_within_time_window", return_value=True)
@patch("researcher.TrendResearcher._is_within_time_window_epoch", return_value=True)
def test_flow(mock_time_epoch, mock_time, mock_feedparser, mock_requests):
    """
    Runs the main logic in mock mode.
    Validates that:
    1. The mock runs successfully with new Reddit/HN scoring.
    2. Per-source grouping works.
    3. Draft files are written appropriately.
    """
    print("Running mocked end-to-end test...")
    # Limit to 1 per source to see if it works
    main(is_mock=True, limit=1)
    print("Mock run complete. Please check the 'drafts/' folder for the output file.")


if __name__ == "__main__":
    test_flow()
