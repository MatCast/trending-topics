# Backlog — Future Enhancements

## Add Limits to Extractions
Add limits to extractions based on the user's tier. For example, users in the free tier can only have 1 extraction at a time, while users in the pro tier can have 5 extractions at a time. This should be based on configurations in the database that determine how many extractions each tier can have at a time.


## Extractions Debugging
Add some debugging instructions on the extractions page so that if users end up having no results, they would have some way to know what to do. Here what we might need to do is, when we do the extraction, we should also create a list of things that can go wrong. For example:
- Things like we got data from the sources but we filtered out because of keywords, time stamps, and so on.
- The data source didn't return any data for the sources.
- The subreddit that you created doesn't exist.
I guess what we can do is to basically log what's going on when the extraction is happening. If the extraction didn't return anything for the source, we can return this back to the front end somehow. Maybe we could store in the extraction; we could store a sub-collection which is called something like "extractions learning" or something like that. We can find out and then we can use this information to give it back to the user in the extraction dashboard.

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
