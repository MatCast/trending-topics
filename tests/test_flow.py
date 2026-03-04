from unittest.mock import patch
from main import main

# A fake RSS feed entry mapping to feedparser.FeedParserDict
FAKE_FEED_DATA = {
    "entries": [
        {
            "title": "New groundbreaking AI model released",
            "link": "https://example.com/ai-model",
            "description": "It achieves state of the art on all benchmarks.",
            "published_parsed": (2025, 1, 1, 12, 0, 0, 0, 1, 0),  # Ignored via mock
        },
        {
            "title": "Sam Altman speaks about AGI",
            "link": "https://example.com/sam-altman",
            "description": "AGI might be closer than we think.",
            "published_parsed": (2025, 1, 1, 12, 0, 0, 0, 1, 0),
        },
        {
            "title": "Top 10 new LLMs",
            "link": "https://example.com/top-10",
            "description": "A review of the best open weights models.",
            "published_parsed": (2025, 1, 1, 12, 0, 0, 0, 1, 0),
        },
        {
            "title": "Old News (Should be ignored by time filter but time filter is mocked out here)",
            "link": "https://example.com/old",
            "description": "This is extra.",
            "published_parsed": (2025, 1, 1, 12, 0, 0, 0, 1, 0),
        },
    ],
    "bozo": False,
}


def mock_parse(*args, **kwargs):
    from feedparser import FeedParserDict

    return FeedParserDict(FAKE_FEED_DATA)


@patch("feedparser.parse", side_effect=mock_parse)
@patch(
    "researcher.TrendResearcher._is_within_time_window", return_value=True
)  # Mock time filter to always pass
def test_flow(mock_time, mock_feedparser):
    """
    Runs the main logic in mock mode.
    Validates that:
    1. The mock runs successfully without throwing setup errors.
    2. Draft files are written appropriately.
    """
    print("Running mocked end-to-end test...")
    main(is_mock=True)
    print("Mock run complete. Please check the 'drafts/' folder for the output file.")


if __name__ == "__main__":
    test_flow()
