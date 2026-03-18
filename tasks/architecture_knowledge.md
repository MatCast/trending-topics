# Full-Stack Application Architecture Knowledge Item

This document serves as a consolidated knowledge base for the project's architectural patterns and structure, transitioning from its legacy CLI roots to a containerized, full-stack application.

## 1. High-Level Architecture
The application runs as a containerized dual-service architecture orchestrated by Docker Compose:
- **Backend**: Python FastAPI serving RESTful endpoints on `localhost:8000`.
- **Frontend**: Nuxt.js (Vue) + DaisyUI + TailwindCSS running on `localhost:3000`/`3001` configured as a Single Page Application (SPA).
- **Database/Auth**: Firebase Firestore for persistence and Firebase Authentication for identity management.

## 2. Environment & Execution Patterns
- **Direct Implementation**: Overarching changes on the full-stack containerized structure are executed directly by the Architect. Subagents and Git worktrees are discouraged for system-wide refactors due to setup overhead and context drift.
- **Docker Compose**: Used as the primary local development environment (`docker-compose.yml`), unifying networking between the Nuxt client and FastAPI backend. **CRITICAL: NEVER run `npm run dev` or `fastapi run` directly on the host machine. Assume the servers are already running within their Docker containers on ports 3000 and 8000.**

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
- **Testing**: Backend tests use `sys.modules`-level mocking of `firebase_admin` so tests run without the SDK installed. 21 tests cover catalog, user source CRUD, extraction, and keyword CRUD.

## 8. Keywords Sub-Collection Architecture
- **Keywords Collection**: Per-user keywords stored in `users/{uid}/keywords/` sub-collection with fields: `text`, `enabled`, `created_at`.
- **Extraction**: `extraction.py` and `scheduler.py` call `list_enabled_keywords(uid)` which queries only `enabled=True` keywords from the sub-collection.
- **Keyword Limits**: `DEFAULT_KEYWORD_LIMITS` maps user tiers to max keywords (`free: 20`, `pro: 100`, `unlimited: -1`). Enforced in `create_keywords()`.
- **API Endpoints**: `GET/POST /api/keywords`, `PUT /api/keywords/{id}`, `POST /api/keywords/bulk` (bulk enable/disable/delete), `DELETE /api/keywords/{id}`.
- **Frontend**: Dedicated `/keywords` management page with table, bulk selection, toggle enabled, comma-separated add input. Keywords removed from `/settings` page.

## 9. Extractions and Results Architecture
- **Extractions Collection**: Metadata for each extraction run is stored in `users/{uid}/extractions/{extraction_id}`. This includes Date, Sources Used, Number of Results, and TTL (`expires_at`).
- **Results Collection (Flat)**: Individual extracted topics are stored in a flat sub-collection `users/{uid}/results/` rather than nested under extractions. They are linked back to the parent via an `extraction_id` field.
- **Why Flat?**: Firestore queries on indexed fields incur read costs purely based on the number of returned documents. Querying a flat collection with `.where('extraction_id', '==', X)` costs exactly the same as querying a sub-collection. However, a flat collection simplifies Cleanup (TTL).
- **TTL & Cleanup**: Both Extractions and Results share standard `expires_at` fields. A single scheduled Cloud Function deletes expired documents from both collections simultaneously without needing complex cascading delete logic.
- **Frontend Dashboard**: The main dashboard `GET /api/extractions` lists extraction history to minimize reads instead of fetching all historical results at once. Clicking an extraction navigates to `/extractions/[id]` to query only that specific `extraction_id`.

## 10. Source Tier Limits (Firestore Driven)
- **Logic**: Enforced primarily on the **enablement** of multi-instance sources (e.g., Reddit) to allow users to catalog as many sources as they wish while capping active processing.
- **Limits**: Stored in `admin/config` in Firestore under `tier_limits`. `DEFAULT_KEYWORD_LIMITS` and `DEFAULT_REDDIT_SOURCE_LIMITS` constants serve as local fallbacks.
- **Enforcement**:
    - **Backend**: Service methods (e.g., `create_source`, `create_keywords`) fetch user's `active_tier` and query Firestore for current limits.
    - **Frontend**: The `sources.vue` page uses the `useUser` composable to fetch dynamic limits. It handles the "unlimited" case (`-1`) by displaying `∞` and bypassing local UI warnings.

## 11. User Profile API
- **Endpoint**: `GET /api/users/me` provides a unified view of the authenticated user's profile.
- **Content**: Includes `uid`, `email`, `active_tier`, `settings`, and the effective `tier_limits` for that user's specific tier.
- **Frontend Integration**: Managed via `useUser.ts` composable. This ensures that when a user's tier is upgraded in the database, the frontend reflects new limits immediately upon profile refresh.

## 12. Deployment Architecture (Google Cloud Run)
- **Services**: Split into `backend-service` (FastAPI) and `frontend-service` (Nuxt Nitro).
- **Auth**: Uses **Application Default Credentials (ADC)**. By running the backend in the same GCP project as Firestore, it inherits permissions automatically via the metadata server, eliminating the need for `service-account.json` in production.
- **Environment Management**: Orchestrated via `env.prod.yaml` files. `gcloud` consumes these via the `--env-vars-file` flag, allowing for discrete, versioned configurations per environment.
- **CORS**: The backend's `FRONTEND_URL` supports comma-separated origins. This allows the backend to serve both the production `.run.app` domain and local `localhost:3000` developers simultaneously.
- **Security**: Services are public at the network layer (`--allow-unauthenticated`) but strictly gated at the application layer via Firebase token verification middleware.
