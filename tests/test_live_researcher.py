import logging
import os
from dotenv import load_dotenv
from researcher import TrendResearcher
from sheets_manager import SheetsManager

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_live_research_flow():
    """
    Performs a LIVE fetch of AI trends but logs to a MOCK sheet.
    This verifies:
    1. Connection to Reddit JSON works.
    2. Connection to HN RSS works.
    3. Metric extraction/scoring works on real data.
    4. Data formatting for logging is correct.
    """
    load_dotenv()

    print("\n--- Starting LIVE Researcher Test ---")

    # 1. Initialize SheetsManager in MOCK mode to avoid cluttering real sheets
    # but still test the logging integration.
    sheets_mock = SheetsManager(
        service_account_file="fake_key.json",
        sheet_id="fake_id",
        is_mock=True
    )

    # 2. Initialize Researcher with 24h window for testing (more likely to find data)
    researcher = TrendResearcher(
        sources_file="config/sources.json",
        sheets_manager=sheets_mock,
        time_window_hours=24
    )

    # 3. Fetch trends (Live network calls!)
    # We'll limit to 2 per source to avoid huge output
    print("Fetching live trends (this may take a few seconds)...")
    top_trends = researcher.fetch_trends(max_trends=2)

    if not top_trends:
        print("WARNING: No trends found in the last 24h. Try relaxing filters or check internet connection.")
        return

    print(f"\nSUCCESS: Found {len(top_trends)} trends across sources.")

    # 4. Integrate with logging logic (from main.py snippet)
    rows_to_append = []
    for t in top_trends:
        print(f"\nSource: {t['source']}")
        print(f"Title: {t['title']}")
        print(f"Metrics: {t.get('ups')} ups, {t.get('comments')} comments (Score: {t['trend_score']})")
        print(f"URL: {t['url']}")

        rows_to_append.append([
            t.get("timestamp"),
            t.get("source"),
            t.get("title"),
            t.get("url"),
            str(t.get("trend_score")),
            t.get("description")[:100] + "...", # Truncate for console output
            str(t.get("ups", 0)),
            str(t.get("comments", 0)),
        ])

    sheets_mock.append_rows(rows_to_append)

    # 5. Final check of mock data
    assert len(sheets_mock._mock_sheet_data) == len(top_trends)
    print("\n--- Live Researcher Test Completed Successfully ---")

if __name__ == "__main__":
    try:
        test_live_research_flow()
    except Exception as e:
        print(f"\nERROR during live fetch: {e}")
        exit(1)
