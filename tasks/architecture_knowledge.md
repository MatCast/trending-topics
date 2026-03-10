# Full-Stack Application Architecture Knowledge Item

This document serves as a consolidated knowledge base for the project's architectural patterns and structure, transitioning from its legacy CLI roots to a containerized, full-stack application.

## 1. High-Level Architecture
The application runs as a containerized dual-service architecture orchestrated by Docker Compose:
- **Backend**: Python FastAPI serving RESTful endpoints on `localhost:8000`.
- **Frontend**: Nuxt.js (Vue) + DaisyUI + TailwindCSS running on `localhost:3000`/`3001` configured as a Single Page Application (SPA).
- **Database/Auth**: Firebase Firestore for persistence and Firebase Authentication for identity management.

## 2. Environment & Execution Patterns
- **Direct Implementation**: Overarching changes on the full-stack containerized structure are executed directly by the Architect. Subagents and Git worktrees are discouraged for system-wide refactors due to setup overhead and context drift.
- **Docker Compose**: Used as the primary local development environment (`docker-compose.yml`), unifying networking between the Nuxt client and FastAPI backend.

## 3. Frontend Architecture (Nuxt.js + DaisyUI)
- **Directory**: `frontend/` (primarily `frontend/app/`).
- **Client-Side Auth & SPA Concept**: Because the application is strictly gated behind a login wall using Firebase Client SDK auth, Server-Side Rendering (SSR) is globally disabled (`ssr: false` in `nuxt.config.ts`).
- **Route Protection**: Implemented via a global router middleware (`auth.global.ts`). Unauthenticated users are seamlessly redirected to `/login` without UI flashes or hydration mismatch errors.
- **State Management**: Uses composables like `useAuth.ts` and `useApi.ts` to manage authentication initialization and backend communication sequentially.
- **UI Components**: Employs DaisyUI strictly for rapid, cohesive, and accessible CSS/Tailwind component styling.

## 4. Backend Architecture (FastAPI)
- **Directory**: `backend/` (logic in `backend/app/`).
- **REST API (`routers/`)**: Distinct router modules separate concerns (e.g., users, sources, integrations).
- **Data Fetching (`parsers/`)**: The monolithic legacy `researcher.py` and `parsers.py` are refactored into distinct class-based parsers per source (e.g., Reddit, Bluesky, IndieHackers).
- **Database Client (`firebase_client.py`)**: Abstracted interface to Firestore. Includes in-memory fallbacks when composite indexing limitations prevent complex queries natively.
- **Data Validation (`models.py`)**: Strict Pydantic models. We ensure defaults are handled correctly (e.g., avoiding Python `None` when dealing with serialized data updates).

## 5. Architectural API Nuances
- **Bluesky API Quirk**: The Bluesky `app.bsky.feed.searchPosts` endpoint fails silently when mixing `OR` query syntax and temporal `since` filters. To fetch accurately, searches are mapped sequentially per keyword and combined.
- **Firestore Limitations**: Cross-field querying (e.g., filtering on `expires_at > X` while ordering by `created_at`) occasionally demands in-memory filtering post-fetch from Firestore to bypass mandatory composite index creation during rapid prototyping.

## 6. Development Workflow loop
1. **Planning Mode**: Any non-trivial task triggers an explicit plan creation in `plan.md`.
2. **Task Validation**: Every bug/feature tracked inside `tasks/todo.md`.
3. **Lessons Learned**: Immediate knowledge capture inside `tasks/lessons.md` after correcting any AI or architectural hurdle (like SPA routing, API limits, Pydantic typing).
4. **Clean Root Hygiene**: Legacy scripts (e.g., orchestrator `main.py` at the root) from the old V1 version should be phased out and ignored for backend API tasks.

## 7. Source Catalog Architecture
- **Catalog Collection**: Top-level `sources/` Firestore collection stores source definitions (name, icon, description, website_url, visibility, config_schema, default_params, is_multi_instance).
- **User Sources**: Per-user subscriptions stored in `users/{uid}/user_sources/` sub-collection with `source_id` references back to the catalog.
- **Catalog Seeding**: Called on app startup via `seed_source_catalog()`. Only creates missing entries — never overwrites existing ones.
- **Visibility Tiers**: Catalog entries have a `visibility` field (`disabled`, `public`, `beta`, `pro`). Currently all are `public`. Future-proofed for user tier filtering.
- **Dynamic Frontend**: All source rendering (sources page, onboarding, dashboard filters/icons) is driven by `GET /api/sources/catalog`. Adding a new source only requires a catalog Firestore doc + a parser class.
- **Testing**: Backend tests use `sys.modules`-level mocking of `firebase_admin` so tests run without the SDK installed. 13 tests cover catalog, user source CRUD, and extraction.
