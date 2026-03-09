---
name: nuxt-ui-docs
description: Fetches and applies documentation for Nuxt UI components, including props, slots, and the theme configuration system for Vue/Nuxt projects.
---

# Nuxt UI Documentation Skill

This skill enables the agent to access the live Nuxt UI documentation to build accessible, high-quality Vue components.

## When to use this skill
- When building UI in a Nuxt 3 project.
- When you need the specific `props` or `slots` API for components starting with `U` (e.g., `<UButton>`, `<UModal>`.
- When configuring the `app.config.ts` for global UI themes.

## How to use it

1. **Access Reference**: Use the browser tool to fetch documentation from:
   - **Main LLM Docs**: `https://ui.nuxt.com/llms.txt`
   - **Full Documentation**: `https://ui.nuxt.com/llms-full.txt`
2. **Contextual Logic**:
   - Check if the project is using **Nuxt UI v2** (Tailwind-based) or **Nuxt UI v3** (built on Tailwind 4/Radix).
   - Prioritize using the `<U...>` component syntax over raw HTML/Tailwind classes where possible.
3. **Theming**:
   - If the user asks for color changes, reference the `ui` prop documentation to modify component-specific styles without breaking the design system.

## Important Constraints
- **Auto-imports**: Remind the user that Nuxt UI components are auto-imported; do not generate manual `import` statements for `UButton`, etc., unless specifically asked.
- **Icons**: Nuxt UI uses the `@nuxt/icon` module. Check `llms.txt` for the correct icon naming convention (e.g., `i-heroicons-magnifying-glass`).

## Reference URLs
- https://ui.nuxt.com/llms.txt
- https://ui.nuxt.com/llms-full.txt