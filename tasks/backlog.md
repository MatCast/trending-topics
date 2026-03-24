# Backlog — Future Enhancements

## DONE: Unified Extraction Settings & Scheduling
Move `time_window_hours` and `max_trends_per_source` from settings to the main extraction dashboard. Implemented a reusable `ExtractionSettings.vue` component to ensure UI consistency between the dashboard, settings page, and the new "Scheduled Extraction" modal. Added "Settings" to the user profile dropdown and removed it from the main navigation menu.


## Add Trackings
Add trackings to the app to track the usage of the app and the usage to understand how the app is used and how to improve it. We should be able to see how many times each API key is used and how many times each source is used. We should also be able to see how many times each user is using the app.

## Add Users Admin Panel
At a user admin panel where I can administrate users' things like the tier they are in, potentially administer what they can do for configurations on the users mostly

## New Story-Rich Sources

These are free RSS-based sources focused on **business storytelling** (founder journeys, lessons, failures, case studies) — not just announcements.

### High Priority
| Source | RSS Feed | Description |
|--------|----------|-------------|
| **Medium** (Entrepreneurship) | `https://medium.com/feed/tag/entrepreneurship` | Personal essays, founder stories, lessons learned. High volume. |
| **Starter Story** | `https://www.starterstory.com/feed` | Founder interviews: "How I built X to $Y/month." Pure storytelling. |
| **The Hustle** | `https://thehustle.co/feed/` | Punchy, viral-style business stories.|

### Medium Priority
| Source | RSS Feed | Description |
|--------|----------|-------------|
| **Harvard Business Review** | `https://hbr.org/resources/rss` | Case studies, leadership stories. More serious but highly shareable. |
| **Fast Company** | `https://www.fastcompany.com/latest/rss` | Innovation stories, company profiles, leadership journeys. |
| **Inc.com** | `https://www.inc.com/rss` | Founder spotlights, "How I Built This" style content. |

---

## DONE: Reddit API Subreddits Fetching
We moved to a Rapid API way of fetching data from Reddit to bypass Cloud Run blocks. It includes a fallback mechanism to the direct API in case the key is missing or the service fails.

### Notes
- All sources use standard RSS feeds → same architecture as `IndieHackersParser` (feedparser-based).
- Medium supports tag-based feeds; other useful tags: `startup`, `business`, `leadership`, `lessons-learned`.
- Consider making `time_window_hours` configurable per source, since some feeds post less frequently than others.

## DONE: Improve Extraction Readiness Check
Fixed the issue where extractions would "hang" in pending. Implemented a real-time Firestore `onSnapshot` listener in the frontend that detects completion and automatically redirects the user to the results page. Requires Firestore Security Rules to be configured for read access.

## DONE: Improve Onboarding Limits Showing
Abstracted limit visibility into a reusable `UsageLimitBadge.vue` component to correctly enforce and display limits (for both keywords and multi-instance sources like Reddit) during the onboarding phase, achieving parity with the main application limits logic.

## DONE: Pre-commit Hook Setup
Configured `.pre-commit-config.yaml` to run `black` and `flake8` dynamically. Tools are installed correctly into the local environment (`linkedin_posts`) instead of polluting the `requirements.txt` for the production container.

## DONE: Add Limits to Extractions
Implemented tier-based extraction quotas (daily, weekly, monthly) and concurrency limits. Users in the free tier are capped at 3 per month and cannot schedule extractions. Pro users are capped at 30 per month. All limits are configurable via Firestore admin config.


---

## DONE: Extractions Debugging
Added debugging instructions on the extractions page. If users end up having no results, they now have visual insights. The backend parsers capture warnings (e.g., filtered by keywords, source didn't return data, subreddit doesn't exist) and save them into an `insights` array in the extraction document. The frontend displays these insights via a dedicated `ExtractionInsights.vue` component, which maintains high-visibility orange alerts for zero-result scenarios and an analytical accordion for partial filtering logs.

## DONE: Consolidated Scheduling UI & Browser Navigation
Unified the scheduling interface by extracting all logic into a reusable `SchedulingForm.vue` component used by both the dashboard modal and the settings page. Integrated the browser's History API to allow the hardware "Back" button to close the modal instead of navigating away. This refactor ensures 100% parity between interfaces and reduces redundant code by over 60%.
