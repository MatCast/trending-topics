# Backlog — Future Enhancements

## Fixes after Migration to neo brutalism

- [x] : The mouse doesn't transform into a pointer when hovering over the "Sign in with Google" button.
- [x] : When you create a new extraction, in the table a new row appears with the new extraction that you just requested. The first date says "Invalid date". That should be changed to the date when the extraction was started. If that's not available yet, just put the current date. Also when you create a new extraction, the number of monthly extractions doesn't change in the top label with the number of extractions.
- [x] : The new extraction button is visible but the button is smaller than the text. Add a plus sign next to the new extraction text to improve UX.
- [ ] The sidebar is not visible on mobile. The whole app turns green, turns grey like an overlay but there is no way to navigate around.

- [ ] The icons of the sources are not consistent between the extractions table and the results table and some of them are missing or incorrect.
- [ ] Make the extraction settings button much smaller and make them on desktop on the same line as the new extraction button.
- [ ] Clicking on the button to schedule your donations doesn't work.
- [ ] The switches to enable or disable something are a bit confusing because the border is the same colour as the deactivated switch, which makes it a bit hard to understand where to click. Ideally let's keep the border black but maybe make the background of the switch grey. Create a component for the switches if there is not already one. Apply this component to all the switches we have. If I remember correctly we have switches in the sources page, in the keywords page, in the settings. If I'm forgetting something, check everywhere we have switches and use the component that we created.
- [ ] In the sources the X button, when you hover over it, the cursor doesn't transform into the pointer and the same happens on the button to add a new subreddit.
- [ ] The disable button for the automation schedule should make every configuration below disappear and display something saying "enable to configure it". Also the button here, which is "Apply schedule", is of a secondary colour. I think it's black with a black border, which is not what I want and we need to make it the primary color.
- [ ] In the keyword page the add button should be yellow and the mouse should become a pointer when hovering over it. Enabling or disabling the keywords, I don't know if it works because the number of active keywords doesn't change on the top. Make sure that the proper calls are made to Firestore to add, enable, disableor delete the keyword that we just added.  Clicking on the selection button next to the header of the keywords table should select all the keywords. Also add an arrow next to the keywords checkbox in the header, which has the features that you can do once the keywords are selected, enable , disable them, delete them similar to gmail. If the user clicks on delete, the pop-up should pop up to ask the user whether they really want to delete them and the delete button should be our red (the same used behind the x button to delete them). Finally if a user adds a keyword which already exists, a pop-up should come up in red like a sonar which says "Keyword already exists".
- [ ] In the sources page: Mouse does not turn to pointer when hovering over the buttons to filter by source. Also the warning for no sources should be of a warning color.
- [ ] When I hover on the sign out, at first the background changes to red quicker, then the font changes to white, which makes it harder to read.


## Extraction Results Timestamps

Make sure that they reflect the actual time stamp of the post or article and not the time stamp when they were extracted.

## DONE: Dynamic Theming System
Implemented a dynamic theme switching system powered by DaisyUI 5 and Nuxt Runtime Config. Replaced hardcoded "dark" themes with a configuration-driven `data-theme` binding. All components now use semantic CSS variables, allowing for instant, application-wide visual changes by updating a single environment variable or config value.

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

## DONE: Mobile Menu & Scheduler Refinement
Resolved visibility issues with the mobile bottom navigation by standardizing DaisyUI 5 `dock-item` classes and increasing z-index. Fixed Vue prop type warnings for the `SchedulerToggle` by implementing robust defaulting and merging logic for the `active` property in the Dashboard and Settings pages. Added layout safeguards (`wrap-break-word`, `overflow-x-hidden`) to ensure responsive breakpoints trigger correctly across all device emulators.
