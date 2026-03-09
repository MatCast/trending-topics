# Backlog — Future Enhancements

## New Story-Rich Sources

These are free RSS-based sources focused on **business storytelling** (founder journeys, lessons, failures, case studies) — not just announcements.

### High Priority
| Source | RSS Feed | Description |
|--------|----------|-------------|
| **Medium** (Entrepreneurship) | `https://medium.com/feed/tag/entrepreneurship` | Personal essays, founder stories, lessons learned. High volume. |
| **Starter Story** | `https://www.starterstory.com/feed` | Founder interviews: "How I built X to $Y/month." Pure storytelling. |
| **The Hustle** | `https://thehustle.co/feed/` | Punchy, viral-style business stories. Great for LinkedIn repurposing. |

### Medium Priority
| Source | RSS Feed | Description |
|--------|----------|-------------|
| **Harvard Business Review** | `https://hbr.org/resources/rss` | Case studies, leadership stories. More serious but highly shareable. |
| **Fast Company** | `https://www.fastcompany.com/latest/rss` | Innovation stories, company profiles, leadership journeys. |
| **Inc.com** | `https://www.inc.com/rss` | Founder spotlights, "How I Built This" style content. |

### Notes
- All sources use standard RSS feeds → same architecture as `IndieHackersParser` (feedparser-based).
- Medium supports tag-based feeds; other useful tags: `startup`, `business`, `leadership`, `lessons-learned`.
- Consider making `time_window_hours` configurable per source, since some feeds post less frequently than others.
