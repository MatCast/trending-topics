# Global Project Context

This file provides critical environment and repository context for you to operate safely.

## Infrastructure
- **Docker**: Use the root `docker-compose.yml` for local development.
  - Backend: `http://localhost:8000` (service name `backend` internally).
  - Frontend: `http://localhost:3000` (service name `frontend` internally).
  - Use `docker-compose build --target development` for dev-specific builds.
- **Secrets**: Do **NOT** hardcode API keys. Use `.env.example` as a template and read from `.env`.

## Project Structure
- **Backend (API)**: Located in `backend/`. This is the primary application logic for the full-stack version. FastApi application.
- **Frontend (UI)**: Located in `frontend/`. Nuxt.js/DaisyUI application.
- `config/`: Configuration files and legacy sources.
- `tasks/`: Project logs, todo lists, and lessons.
- `plan.md`: The current master plan. Always respect it.

## Coding Standards
- Write tests in `tests/` for new functionality.
