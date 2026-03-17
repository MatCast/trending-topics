# Project Plan

This is the Single Source of Truth for the Architect and sub-agents. Both should refer to and update this document to track progress.

## Phases
* Phase 1 (Scaffolding): [Completed]
* Phase 2 (Backend/Core): [Phase 2.3 Completed - Firestore Tier Migration & User Profile API]
* Phase 3 (Frontend/Formatting): [Phase 3.1 Completed - Basic UI & Settings]
* Phase 4 (Containerization): [Completed]

## Active Tasks
* [ ] **Subagent 1: Backend Priority** - Move extraction to background tasks and add 'pending' Firestore document initialization. Update endpoint to return instantly.
* [ ] **Subagent 2: Frontend Priority** - Hook up Firestore onSnapshot listener to the `/extractions` dashboard to update polling UI state without locking main thread.

## Agent Tracking & Context
* **Subagent 1**: *Pending* (Backend Extraction Background Job)
* **Subagent 2**: *Pending* (Frontend Realtime UI Listener)

*Note to Architect: Ensure each sub-agent is assigned strict files and an isolated goal to prevent context drift.*
