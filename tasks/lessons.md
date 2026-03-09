# AI Architect Lessons & Learnings

This file acts as the continuous learning memory base for the Architect agent.
Whenever a sub-agent fails a task, struggles with a specific dependency, or when a workflow strategy is proven ineffective, the Architect must document the lesson here.

The Architect must read this file at the start of every session to avoid repeating mistakes.

## Lessons
1. **Direct Implementation vs Sub-agents**: For tasks involving complex orchestration (like Docker Compose across multiple services), the user may prefer direct implementation by the Architect to ensure consistency and avoid environment/CLI overhead. Use sub-agents for more isolated, atomic tasks.
2. **Firestore Composite Indexes**: Range filters on multiple fields (e.g., `expires_at > now` and `order_by("created_at")`) require composite indexes. If indexes cannot be created, filter by the primary criteria in Firestore and apply supplementary filters (like expiration checks) in memory after streaming results.
3. **Pydantic Validation Sensitivity**: When returning lists of objects through FastAPI, ensure every object contains all required fields (e.g., `id`). In-place dictionary updates in backend clients can ensure returned lists are valid for Pydantic response models.
4. **Frontend validation visibility**: Always provide immediate visual feedback (e.g., `input-error` class and error labels) when input validation fails, especially for uniqueness or formatting, to prevent user confusion.
5. **Nuxt SPA and Client-Side Auth**: When building a Nuxt app entirely behind a client-side authentication wall (like Firebase Client SDK), global SSR should be disabled (`ssr: false` in `nuxt.config.ts`). Attempting to SSR protected pages causes severe layout-breaking hydration mismatches when the client subsequently redirects to the login page.
6. **Full-Stack App Architecture**: Do not spawn subagents or use git worktrees when operating on a full-stack containerized app. Make changes directly in the main repository environment. Furthermore, ensure old CLI scripts and non-containerized code from previous iterations are completely removed to maintain a clean root directory.
7. **Bluesky API Search Constraints**: The Bluesky `app.bsky.feed.searchPosts` endpoint silently returns 0 results when an `OR` query (e.g. `AI OR Agent`) is combined with a `since` timestamp filter when sorting by `top`. To circumvent this, iterate over individual keywords and merge/deduplicate the results manually.
8. **Pydantic `None` vs Missing Keys**: When Pydantic models with `Optional` fields are serialized via `model_dump()`, fields default to `None` rather than being omitted. This means `dict.get("key", fallback)` returns `None` (not the fallback), because the key exists. Use `dict.get("key") or fallback` instead when a truthy default is required.
