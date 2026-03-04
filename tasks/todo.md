# AI Trend-to-LinkedIn Automation Todo

## 1. Project Initialization
- [x] Initialize Git repository.
- [x] Create `.gitignore` (ignore `.env`, `*.json`, `__pycache__`, `drafts/`, `prompts/`).
- [x] Create `requirements.txt` (`google-genai`, `feedparser`, `gspread`, `python-dotenv`).
- [x] Set up `config/` directory with `sources.json` and `templates.json`.
- [x] Create `.env.example` placeholder.

## 2. Implement Sub-modules
- [x] Create `sheets_manager.py` with mock capability.
  - Features: Auth via service account, append row `[Timestamp, Source, Title, URL, TrendScore]`, dedup URLs.
- [x] Create `researcher.py`.
  - Fetch RSS feeds for reddit (`/rising.rss`) and HN.
  - Filter last 3 hours.
  - Extract relevant fields and dedup globally.
  - Define how "Top 3 trending topics" are scored/sorted.
- [x] Create `drafter.py`.
  - Integrate `google-genai` (Gemini 3 Flash).
  - Draft 3 variations using `templates.json` for each of the top 3 trending topics.

## 3. Orchestration
- [x] Create `main.py`.
  - Fetch trending topics.
  - Log to sheet.
  - Generate drafts.
  - Save drafts to local `drafts/` directory.

## 4. Verification
- [x] Write a test script or mock invocation (`tests/test_flow.py`).
- [x] Verify execution without making actual API calls to Live Google Sheets or real Gemini (if desired, though real AI API might be okay if credentials provided; default to offline verify mode first).

