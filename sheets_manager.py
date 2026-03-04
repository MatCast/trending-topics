import gspread
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SheetsManager:
    """Manages appending rows and deduplicating URLs in Google Sheets.
    Contains logic for mocking interactions during tests."""

    def __init__(self, service_account_file: str, sheet_id: str, is_mock: bool = False):
        self.is_mock = is_mock
        self.sheet_id = sheet_id
        self._mock_sheet_data: List[List[str]] = []

        if not self.is_mock:
            try:
                self.gc = gspread.service_account(filename=service_account_file)
                # In a real environment, you'd open by URL/ID:
                # self.spreadsheet = self.gc.open_by_key(self.sheet_id)
                # self.worksheet = self.spreadsheet.sheet1
                logger.debug("SheetsManager initialized in LIVE mode.")
            except Exception as e:
                logger.error(f"Failed to initialize live SheetsManager: {e}")
                raise
        else:
            logger.debug("SheetsManager initialized in MOCK mode.")

    def get_existing_urls(self) -> set[str]:
        """Fetch all URLs currently in the sheet to prevent duplicates.
        Assumes URL is in column 4 (index 3)."""
        if self.is_mock:
            return {row[3] for row in self._mock_sheet_data if len(row) > 3}

        # Live implementation:
        try:
            # records = self.worksheet.get_all_values()
            # return {row[3] for row in records[1:] if len(row) > 3}  # Skip header
            logger.warning("Live get_existing_urls not fully implemented, returning empty set.")
            return set()
        except Exception as e:
            logger.error(f"Failed to fetch existing URLs: {e}")
            return set()

    def append_rows(self, rows: List[List[str]]) -> None:
        """Appends multiple rows to the Google Sheet.
        Row format: [Timestamp, Source, Title, URL, TrendScore]"""
        if not rows:
            return

        if self.is_mock:
            self._mock_sheet_data.extend(rows)
            logger.info(f"[MOCK] Appended {len(rows)} rows to sheet.")
            return

        # Live implementation:
        try:
            # self.worksheet.append_rows(rows)
            logger.info(f"[LIVE] Appended {len(rows)} rows to sheet {self.sheet_id}.")
        except Exception as e:
            logger.error(f"Failed to append rows to live sheet: {e}")
            raise
