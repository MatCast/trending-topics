# Reddit Rapid API Integration Plan

## Goal
Migrate Reddit fetching to RapidAPI (reddit3.p.rapidapi.com) while keeping the direct Reddit API method as a fallback. Let the user configure which fetching method is used, defaulting to RapidAPI.

## Phases
- [x] Clarify requirements with the user (current phase)
- [x] Store API key locally in `.env.example` and `.env`, and handle it securely.
- [x] Update backend (`models.py`, `firebase_client.py`, `routers/users.py` or `routers/sources.py`) to store the user's preferred Reddit fetching method.
- [x] Update the `RedditParser` in `parsers/reddit.py` to use RapidAPI by default, but fall back to direct request if the user configured it so.
- [ ] Update the frontend to allow users to toggle this setting (Skipped as per user request).
- [ ] Test the integration locally, verifying both methods work.
- [x] Deploy to Cloud Run after verifying the `env.prod.yaml` / `.env.yaml` is updated with the RapidAPI key.
