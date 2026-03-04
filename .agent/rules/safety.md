---
trigger: always_on
---

# Git and Security Protocol
- **Git Hygiene**: Always initialize a repository with a professional `.gitignore` (ignore `.env`, `*.json` keys, `__pycache__`, `.venv`).
- **Zero-Credential Policy**: You are forbidden from asking for or hardcoding actual API keys. Use placeholders and provide a `.env.example` file instead.
- **Code Only**: Your goal is to write, test (with mocks), and verify the code. Do not perform live writes to external Google Sheets during the build phase.