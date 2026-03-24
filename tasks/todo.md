# Task: Unified Extraction Settings & Scheduling

## Plan
- [x] Initial Research & Backlog Update
- [x] Create reusable `ExtractionSettings.vue` component
- [x] Implement settings toolbar on Dashboard (`index.vue`)
- [x] Implement "Scheduled Extraction" modal
- [x] Update user profile dropdown in `default.vue`
- [x] Remove "Settings" from main navigation
- [x] Refactor `settings.vue` using the new component
- [x] Verify responsiveness and auto-saving logic
- [x] Refinement: Make settings labels clickable to focus inputs
- [x] Refinement: Separate 'New Extraction' and 'Schedule' buttons on Dashboard

## Separation of Manual vs Scheduled Settings
- [x] Backend: Update `ScheduleConfig` in `models.py` (Add `active`, params, `last_run`)
- [x] Backend: Refactor `run_scheduled_extractions` (Check `active`, Fallback params)
- [x] Backend: Implement `last_run_at` update in scheduler
- [x] Frontend: Refactor `ScheduledExtractionModal.vue` (Internal settings & Toggle)
- [x] Frontend: Update `index.vue` to handle nested schedule save
- [x] Frontend: Update `settings.vue` for consistent nested data handling
- [x] Verification: Test independent setting persistence
- [x] Verification: Verify scheduled run fallback to global settings
- [x] UI: Move "Activate" toggle to top and implement conditional layout
- [x] UI: Implement auto-save on toggle click
- [x] UI: Create unified `SchedulerToggle.vue` component and centralized date formatting
- [x] UI: Consolidate scheduling UI into a single `SchedulingForm.vue` component for Modal and Settings
