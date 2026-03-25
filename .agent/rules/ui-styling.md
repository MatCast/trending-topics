---
trigger: model_decision
description: Use this ure when making changes to the UI and the frontend
---

# UI & Styling Guidelines: Neobrutalism Vue

You are an expert Nuxt 3 and Vue developer. Your primary directive for UI is to STRICTLY use the `neobrutalism-vue` component library (which is built on top of `shadcn-vue` and Reka UI).

## Core Directives:
1. **NO CUSTOM UI:** Do NOT reinvent the wheel. If the app needs a menu, use the Sidebar or Navigation Menu component. If it needs a list of news, use the Table, Card, or Scroll Area component.
2. **STRICT ADHERENCE:** Use the components exactly as they appear in the neobrutalism-vue documentation. Do not add highly personalized Tailwind classes or arbitrary styles.
3. **STYLE OVERRIDES:** The only permitted customizations are global variables in `tailwind.config.ts` (colors, border-radius) or layout-level spacing (margins/padding between standard components).
4. **DOCUMENTATION SOURCE OF TRUTH:** Always refer to the official documentation structure.
   - Shadcn Vue LLM Docs: `https://www.shadcn-vue.com/llms.txt`
   - Neobrutalism Vue Registry: `https://neobrutalism-vue.com/`
5. **INSTALLATION:** When instructed to add a component, ALWAYS use the registry CLI:
   `npx shadcn-vue@latest add https://neobrutalism-vue.com/r/[component-name].json`

## Design Rules:
- **Borders:** Thick, defined borders (`border-2` or `border-3` with `border-black`).
- **Corners:** No rounding unless globally specified.