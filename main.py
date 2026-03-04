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


def main(is_mock: bool = False):
    logger.info(f"Starting AI Trend-to-LinkedIn Automation (Mock Mode: {is_mock})")
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

    drafter = ContentDrafter(templates_file="config/templates.json")

    # 2. Fetch Top 3 Trending Topics
    top_trends = researcher.fetch_trends()
    if not top_trends:
        logger.info("No new trending topics found in the last 3 hours.")
        return

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
            ]
        )
    sheets_manager.append_rows(rows_to_append)

    # 4. Generate Drafts
    logger.info("Generating drafts for top trends...")
    drafts_text = drafter.generate_all_drafts(top_trends, is_mock=is_mock)

    # 5. Save output
    os.makedirs("drafts", exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"drafts/{timestamp_str}.txt"

    with open(filename, "w") as f:
        f.write(drafts_text)

    logger.info(f"Successfully wrote drafts to {filename}")


if __name__ == "__main__":
    import sys

    # Pass --live to run the live mode
    run_live = "--live" in sys.argv
    main(is_mock=not run_live)
