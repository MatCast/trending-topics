# AI Architect Lessons & Learnings

This file acts as the continuous learning memory base for the Architect agent.
Whenever a sub-agent fails a task, struggles with a specific dependency, or when a workflow strategy is proven ineffective, the Architect must document the lesson here.

The Architect must read this file at the start of every session to avoid repeating mistakes.

## Lessons
1. **Direct Implementation vs Sub-agents**: For tasks involving complex orchestration (like Docker Compose across multiple services), the user may prefer direct implementation by the Architect to ensure consistency and avoid environment/CLI overhead. Use sub-agents for more isolated, atomic tasks.
