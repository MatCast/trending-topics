# AI Trend-to-LinkedIn Automation

A modular Python system that identifies trending AI news from RSS feeds (Reddit, Hacker News) and generates distinct LinkedIn post drafts using Google Gemini (Gemini 3 Flash).

## Features
- **Smart Researcher**: Fetches trends from multiple sources, filters by time (last 3 hours), deduplicates URLs, and uses keyword filtering.
- **Engagement-Aware Scoring**: Ranks topics based on discussions and source weights.
- **AI Drafter**: Generates 3 distinct LinkedIn versions for each topic (Specialist, Strategist, Provocateur) using the latest Gemini models.
- **Google Sheets Integration**: Automatically logs trending topics to a spreadsheet for tracking.
- **Development-Ready**: Integrated with `virtualenvwrapper` and VSCode for a smooth developer experience.

## Quick Start

### 1. Project Setup
```bash
# Clone the repository
git clone <repo-url>
cd LinkedInPosts

# Create and activate environment (using virtualenvwrapper)
mkvirtualenv -p python3.11 linkedin_posts

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Fill in your credentials in the `.env` file (see [GCP Setup Guide](.system_generated/gcp_setup_guide.md) for details).
3. Customize your sources and styles in `config/sources.json` and `config/templates.json`.

### 3. Running the Automation

#### Mock Mode (Safety First)
Run the system without making actual API calls to Gemini or Google Sheets:
```bash
python3 main.py
```

#### Live Mode
Run the full automation and publish to your Google Sheet:
```bash
python3 main.py --live
```

#### Advanced CLI Options
- `--limit N`: Override the number of topics to process (e.g., `--limit 5`). This bypasses the `MAX_TOP_TRENDS` environment variable.
- `--no-draft`: Only run research and log trends to Google Sheets, skipping Gemini draft generation.
- `--live`: Use live credentials; omit for a mocked run.

Example (Research 5 topics and log them only):
```bash
python3 main.py --live --limit 5 --no-draft
```

## Project Structure
- `main.py`: The orchestrator.
- `researcher.py`: RSS fetching and trend analysis.
- `drafter.py`: Gemini-powered content generation.
- `sheets_manager.py`: Google Sheets interface.
- `config/`: JSON configuration for sources and templates.
- `drafts/`: Local storage for generated post drafts.
- `tests/`: Offline verification suite.

## VSCode Integration
This repository includes:
- `.vscode/settings.json`: Automatically picks up the `linkedin_posts` virtual environment.
- `.vscode/launch.json`: Pre-configured debug targets for Mock and Live modes.
