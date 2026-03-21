# Improve Onboarding Tier Limits Plan

## Goal
Improve the onboarding page (`frontend/app/pages/onboarding.vue`) to respect user tier limits for keywords and sources (specifically Reddit), making it consistent with how limits are shown and enforced in the main application (`keywords.vue` and `sources.vue`).

## Tasks
- [x] Initialize Plan and Research Current Implementation
- [x] Create Reusable Component `UsageLimitBadge.vue`
  - [x] Implement generic limit badge with warning support.
- [x] Implement Keyword Limits in Onboarding & Main App
  - [x] Fetch user profile via `useUser()` in onboarding.
  - [x] Use `UsageLimitBadge` in `onboarding.vue` and `keywords.vue`.
  - [x] Prevent adding keywords beyond the limit in onboarding.
- [x] Implement Source Limits in Onboarding & Main App
  - [x] Add computed properties for Reddit limits in onboarding.
  - [x] Use `UsageLimitBadge` in `onboarding.vue` and `sources.vue`.
  - [x] Update `addDraftInstance` in onboarding to add new subreddits as disabled if limit is reached.
- [ ] Verify Changes
- [ ] Finalize Documentation (Backlog, Lessons, Architecture)
