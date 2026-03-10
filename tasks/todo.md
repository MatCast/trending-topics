# Trending News Finder

## Automation Todo

## 1. Project Initialization
- [x] Initialize Git repository.
- [x] Create `.gitignore` (ignore `.env`, `*.json`, `__pycache__`, `drafts/`, `prompts/`, `keys/`).
- [x] Create `requirements.txt` (`google-genai`, `feedparser`, `gspread`, `python-dotenv`).
- [x] Set up `config/` directory with `sources.json` and `templates.json`.
- [x] Create `.env.example` placeholder.

## 2. Implement Sub-modules
- [x] Create `sheets_manager.py` with mock capability.
- [x] Create `researcher.py`.
- [x] Create `drafter.py`.

## 3. Orchestration & Config
- [x] Create `main.py` orchestrator with `research_and_log` modularity.
- [x] Implement CLI flags using `argparse` (`--live`, `--limit`, `--no-draft`).
- [x] Configure VSCode environment and debugger.
- [x] Add configurable trend limit (`MAX_TOP_TRENDS`).

## 4. Documentation
- [x] Create GCP Setup Guide.
- [x] Create README.md.

## 5. Verification
- [x] Write mock test suite.
- [x] Verify local generation works.

## 6. Multi-Agent Architecture
- [x] Create `.agent/rules/architect.md` (Main Agent Rules).
- [x] Create `headless.md` (Gemini CLI Sub-agent Rules).
- [x] Create `plan.md` (Shared State / Single Source of Truth).
- [ ] Enable Terminal Access (Auto) for Antigravity Agent in UI.

## 7. Containerization
- [x] Create `docker-compose.yml` for local orchestration.
- [x] Update `backend/Dockerfile` for local development (multi-stage).
- [x] Update `frontend/Dockerfile` for local development (multi-stage).
- [x] Verify local connectivity between services.
- [x] Add health check endpoints to both services.

# 8. Indie Hackers Source

- [x] Add free Indie Hackers source

# 9. Rework how sources are stored
This is to be defined and not implemented until a clear plan is established.

- [ ] Define a new way to store sources.
- [ ] Make sources own collection with data which are the same for all users (urls, icons etc. ). This would also allow the frontend to display any new source added to the DB.
- [ ] Implement the new way to store sources.

## Bugs
- [x] Make reddit rubreddits unique: a user cannot add a subreddit which is already added.
- [x] In settings: when a user adds a keyword simply adding it or removing it should make the change take effect without having to save.
- [x] Implement ascending/descending sorting in extraction dashboard.
- [x] Implement authentication protection on all frontend routes except /login.
- [x] Fix Bluesky extraction not returning data due to API 'since' + 'OR' keyword bug.

## 10. Reddit OAuth & Rate Limits
- [x] Plan and Architectural Review
- [ ] Backend Implementation (Reddit Auth router, Token storage in Firestore)
- [ ] Backend Implementation (Parser update to use OAuth token, Enforce Tier limits)
- [ ] Frontend Implementation (Connect Reddit button, Callback page handling)
- [ ] Verification (Local OAuth flow, Tier limit testing)
