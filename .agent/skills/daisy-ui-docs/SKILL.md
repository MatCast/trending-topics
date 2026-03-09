---
name: daisy-ui-docs
description: Provides the agent with the latest daisyUI component documentation, Tailwind v4 compatibility notes, and code snippets from the official daisyUI LLM endpoint.
---

# daisyUI Documentation Skill

This skill allows the agent to retrieve and apply official daisyUI documentation to ensure UI components are built using the correct Tailwind CSS class names and the latest version (v5+) standards.

## When to use this skill
- Use this when building or refactoring frontend components using Tailwind CSS and daisyUI.
- Use this when you need specific component syntax (e.g., Modals, Drawers, Navbar).
- Use this if you encounter styling issues that might be related to daisyUI versioning (e.g., Tailwind v4 migration).

## How to use it

1. **Retrieve Context**: Whenever the user asks for a daisyUI component, navigate to `https://daisyui.com/llms.txt`
2. **Analyze Content**:
   - Look for the specific component class names.
   - Note the hierarchy (component -> part -> style -> color).
   - Check for "install notes" if the project setup is being questioned.
3. **Generate Code**:
   - Use the semantic class names provided in the documentation (e.g., `btn-primary`, `card-title`).
   - Ensure the output follows the latest "component-first" approach of daisyUI.

## Reference URLs
- Main LLM Docs: https://daisyui.com/llms.txt
- Detailed Setup: https://daisyui.com/docs/editor/gemini/

## Implementation Guide for the Agent
- Always verify if the user is using Tailwind v4, as daisyUI 5 requires it.
- If the user provides a design requirement, search the `llms.txt` for the most appropriate component match.