---
description: How to control the gemini CLI efficiently as a Sub-Agent worker
---

# Gemini CLI Sub-agent Instructions

This skill acts as a manual for the Main Architect Agent to spawn and control Gemini CLI sub-agents safely in parallel.

## Parallel Execution (Git Worktrees)
**CRITICAL:** When spawning multiple sub-agents to work on different tasks simultaneously, they **MUST NOT** share the same working directory. They will overwrite each other's git active branches. You must use `git worktree`.

**Workflow for spawning a parallel worker:**
1. Create a worktree for the task: `git worktree add ./workers/feature-name -b subagent/feature-name`
2. Spawn the gemini sub-agent inside that worktree: `gemini "Task description" --cwd ./workers/feature-name --non-interactive`
3. After the worker completes, navigate to the worktree, review the diff, and commit the changes if they look good (or have the worker commit them).
4. Merge the branch into main from the root directory: `git merge subagent/feature-name`
5. Cleanup the worktree: `git worktree remove ./workers/feature-name`

## Commands & Best Practices
* `gemini "task"`: Standard command to execute a task.
* `gemini -m gemini-2.0-flash "task"`: Use the fast model for workers.
* `--non-interactive`: **ALWAYS** run with this flag to prevent terminal hanging.
* `--files <file1>`: Pass specific context files to the sub-agent.
* **Complex Prompts**: For complex tasks, write instructions to a file (e.g., `echo "do this" > /tmp/task.txt`) and run `gemini "$(cat /tmp/task.txt)"`.

## Protocol for Architect (You)
1. Write isolated instructions and create a git worktree.
2. Spawn the worker using `--cwd` to point to the worktree.
3. Wait for the CLI command to finish.
4. Review outputs via `git diff main..subagent/feature-name`.
5. Update `plan.md` and `tasks/lessons.md` based on the result.
