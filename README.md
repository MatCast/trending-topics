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

### CLI Command Reference

The `main.py` script supports several flags to customize how the automation runs:

| Flag | Description | Default |
| :--- | :--- | :--- |
| `--live` | Run in LIVE mode (uses real Gemini and Google Sheets APIs). | Mock Mode |
| `--limit N` | Max trends to fetch **per source**. | `MAX_TOP_TRENDS` (env) or 3 |
| `--hours N` | Lookback window in hours for trends. | `TIME_WINDOW_HOURS` (env) or 3 |
| `--no-draft` | Only research and log trends; skip AI draft generation. | False |
| `--no-filter` | Disable AI-related keyword filtering (fetches all rising content). | True (filtering enabled) |

#### Examples

**1. Daily AI Pulse (Last 3 hours, keyword filtered):**
```bash
python3 main.py --live --limit 3
```

**2. Broad Trend Research (Last 24 hours, no keyword filter, no drafting):**
```bash
python3 main.py --live --hours 24 --no-filter --no-draft
```

**3. Safety Calibration (Mocked run with high volume):**
```bash
python3 main.py --limit 10
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
