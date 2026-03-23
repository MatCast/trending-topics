# Task: Create Subagent Delegation Architecture

## Plan
- [x] Brainstorm parallel subagent workflow using Agent Profiles and Git Worktrees.
- [x] Create `.agent/profiles/frontend-expert.md` with boundaries and skills.
- [x] Create `.agent/profiles/backend-expert.md` with boundaries and Docker test commands.
- [x] Create `.agent/skills/architect-delegation/SKILL.md` detailing the Architect's role in creating API contracts, making worktrees, passing correct profiles, and running parallel UI/API agents without port conflicts using `docker compose run`. 

## Docker Parallelization Strategy
- Worktrees inherently have their own directory names, so `docker-compose` creates unique, isolated project networks (e.g. `backendfeature_backend_run_xxx`).
- Subagents are instructed to use `docker compose run --rm <service> <command>` instead of `docker compose up`. This ensures they can run tests without binding to host ports (like 8000/3000), avoiding conflicts with the main development environment or each other.
