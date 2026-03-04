---
name: ai-trend-orchestrator
description: Generates Python code to fetch AI trends (RSS), log to Google Sheets, and draft LinkedIn posts via Gemini.
triggers:
  - "build the AI trend bot"
  - "create the LinkedIn content automation"
capabilities:
  - python_scripting
  - logic_design
---

# Mission
Create a modular Python system that automates the discovery of AI trends and drafts content.

# Architectural Instructions
1. **Config-Driven**: The code must read subreddits from `config/sources.json` and post templates from `config/templates.json`.
2. **Modular Scripts**:
    - `researcher.py`: Handles RSS fetching (Reddit/HN) and temporal filtering (3-hour window).
    - `sheets_client.py`: Wrapper for `gspread` using Service Account auth via `SERVICE_ACCOUNT_FILE` env var.
    - `drafter.py`: Interface for `google-genai` to create 2-3 versions of posts.
    - `main.py`: Entry point orchestrating the flow.
3. **Security**: All API keys and file paths for credentials MUST be pulled from `.env` or system environment variables. Never hardcode them.
4. **Drafting Logic**: Use the `gemini-3-flash` model for high-speed, cost-effective generation.