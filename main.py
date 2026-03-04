import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from sheets_manager import SheetsManager
from researcher import TrendResearcher
from drafter import ContentDrafter

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def research_and_log(is_mock: bool = False, limit: int = None):
    """Fetches trending topics and logs them to Google Sheets, without drafting."""
    logger.info(f"Starting Research & Log Only (Mock Mode: {is_mock}, Limit: {limit})")
    load_dotenv()

    # 1. Initialize logic
    service_account_file = os.environ.get(
        "SERVICE_ACCOUNT_FILE", "mock_service_account.json"
    )
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "mock_sheet_id")

    sheets_manager = SheetsManager(
        service_account_file=service_account_file, sheet_id=sheet_id, is_mock=is_mock
    )

    researcher = TrendResearcher(
        sources_file="config/sources.json",
        sheets_manager=sheets_manager,
        time_window_hours=3,
    )

    # 2. Fetch Trending Topics
    top_trends = researcher.fetch_trends(max_trends=limit)
    if not top_trends:
        logger.info("No new trending topics found.")
        return []

    # 3. Log to Google Sheets
    rows_to_append = []
    for t in top_trends:
        rows_to_append.append(
            [
                t.get("timestamp"),
                t.get("source"),
                t.get("title"),
                t.get("url"),
                str(t.get("trend_score")),
                t.get("description"),
                str(t.get("ups", 0)),
                str(t.get("comments", 0)),
            ]
        )
    sheets_manager.append_rows(rows_to_append)
    return top_trends


def main(is_mock: bool = False, limit: int = None, no_draft: bool = False):
    """Main flow coordinating research, logging, and drafting."""
    # 1. Research and Log
    top_trends = research_and_log(is_mock=is_mock, limit=limit)

    if not top_trends or no_draft:
        if no_draft:
            logger.info("Drafting skipped as requested.")
        return

    # 2. Initialize Drafter
    drafter = ContentDrafter(templates_file="config/templates.json")

    # 3. Generate Drafts
    logger.info("Generating drafts for top trends...")
    drafts_text = drafter.generate_all_drafts(top_trends, is_mock=is_mock)

    # 4. Save output
    os.makedirs("drafts", exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"drafts/{timestamp_str}.txt"

    with open(filename, "w") as f:
        f.write(drafts_text)

    logger.info(f"Successfully wrote drafts to {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Trend-to-LinkedIn Automation")
    parser.add_argument("--live", action="store_true", help="Run in live mode (using real API keys and sheets)")
    parser.add_argument("--limit", type=int, help="Override the maximum number of topics to process")
    parser.add_argument("--no-draft", action="store_true", help="Only research and log trends, skip generating drafts")

    args = parser.parse_args()

    main(is_mock=not args.live, limit=args.limit, no_draft=args.no_draft)
