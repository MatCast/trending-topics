# Backlog — Future Enhancements

## Improve Extraction Readiness Check
Currently when you create an extraction, the extraction hangs in pending as long as the user doesn't refresh the page. We should make this different. As soon as the data changes in Firebase from pending to completed, we should move the extraction to completed and fetch also all the data related to the extraction, so the number of results, the sources, and so on.

## Improve Onboarding Limits Showing
Currently when you do the onboarding, you are not aware of how many keywords you can add and so on. Also you can add as many as you want even if you are on a non-paying tier so we should change that.

## Extractions Debugging
Add some debugging instructions on the extractions page so that if users end up having no results, they would have some way to know what to do.

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
