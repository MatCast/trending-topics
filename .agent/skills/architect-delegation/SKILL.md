---
description: How to orchestrate specialized subagents in parallel using Worktrees and Profiles.
---

# Architect Subagent Delegation Skill

This skill teaches the Lead Architect (You) how to delegate complex tasks (like full-stack features) into specialized, parallel worker streams without conflicts.

## 1. Define the Contract
Before spawning workers, you must define the explicit interface between them.
- If it's a full-stack feature, write a `specs/api-contract-for-feature-X.md` detailing the exact JSON request/response schema.

## 2. Prepare Isolated Contexts
Workers are highly specialized and stupid outside of their domain. Do NOT give them the global `todo.md` unless necessary.
- Create a specific task file for the frontend: `echo "Implement UI for feature X using specs/api-contract-for-feature-X.md" > /tmp/frontend-task.md`
- Create a specific task file for the backend: `echo "Implement API endpoint for feature X adhering to specs/api-contract-for-feature-X.md" > /tmp/backend-task.md`

## 3. Spawn Parallel Worktrees
To prevent Git conflicts and file locks, workers MUST run in separate directories.
1. `git worktree add ./workers/frontend-feature -b feature-frontend`
2. `git worktree add ./workers/backend-feature -b feature-backend`

## 4. Execute Specialized Profiles
You have predefined agent profiles in `.agent/profiles/`. Use them to lock the workers into their domain. Pass the profile as a `--files` argument to the `gemini` CLI. Be exceptionally clear to pass the specific, focused task file.
If you need to use gemini cli, use the `gemini-cli` skill to review the documentation.

**Run Backend Worker (Parallel Terminal 1):**
```bash
cd ./workers/backend-feature && gemini --files ../../.agent/profiles/backend-expert.md -y "$(cat /tmp/backend-task.md)"
```

**Run Frontend Worker (Parallel Terminal 2):**
```bash
cd ./workers/frontend-feature && gemini --files ../../.agent/profiles/frontend-expert.md -y "$(cat /tmp/frontend-task.md)"
```

## 5. Testing & Docker Safety
- The profiles explicitly instruct workers to use `docker compose run --rm <service> <cmd>` instead of `docker compose up`. This ensures they test their code in isolated containers without crashing due to host port bindings (3000/8000).
- Example payload inside the task prompt for the backend subagent: *"Ensure you run tests on your logic using `docker compose run --rm backend pytest` before finishing."*

## 6. Review and Merge
- Once workers complete their tasks, return to the root of your repository and ensure you are on your primary integration branch (e.g., `git checkout main`).
- Run a global `git fetch` or `git status` if needed.
- Merge the workers' isolated branches:
  - `git merge feature-frontend`
  - `git merge feature-backend`
  *(Note: Since you restricted their directories via profiles, there should be zero merge conflicts!)*
- Clean up the worktrees to save space:
  - `git worktree remove ./workers/frontend-feature`
  - `git worktree remove ./workers/backend-feature`
  - `git branch -d feature-frontend feature-backend` (optional, to clean up branches)
- Update your global tracker and `tasks/lessons.md` upon any errors made by the workers so you remember for next orchestration.
