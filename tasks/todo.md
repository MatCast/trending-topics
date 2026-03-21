# Improve Extraction Readiness Check Plan

## Goal
Improve the extraction readiness check. Currently, extractions stay in "pending" until the page is refreshed. We need to implement real-time updates using Firestore listeners so the UI updates automatically when an extraction is completed.

## Proposed Changes

### Frontend
- [ ] Investigate `frontend/app/pages/index.vue` (or wherever extractions are listed) to see current fetching logic.
- [ ] Add Firestore listener to the active extraction.
- [ ] Trigger a data refresh for that specific extraction once the status changes to `completed`.

### Backend
- [ ] Review `backend/app/routers/extraction.py` to ensure the status is properly updated in Firestore.
- [ ] Ensure `results_count` and `sources` are updated in the extraction document.

## Tasks
- [/] Initialize Plan and Research Current Implementation
- [ ] Research Frontend Extraction Listing
- [ ] Research Backend Extraction Status Updates
- [ ] Implement Firestore Listener in Frontend
- [ ] Verify Real-time Updates
- [ ] Finalize Documentation (Backlog, Lessons, Architecture)
