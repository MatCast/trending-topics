# Global Project Context (Sub-agents)

This file provides critical environment and repository context for you to operate safely.

## Python Environment
- **Virtualenv**: Use `virtualenvwrapper` (workspace: `workon linkedin_posts`).
- **Paths**: Always use absolute paths for execution if possible:
  - Python: `/home/gozy4/.virtualenvs/linkedin_posts/bin/python`
  - Pip: `/home/gozy4/.virtualenvs/linkedin_posts/bin/pip`
- **Rule**: Never install packages globally. Always use the specified virtualenv.

## Infrastructure
- **Docker**: Use the root `docker-compose.yml` for local development.
  - Backend: `http://localhost:8000` (service name `backend` internally).
  - Frontend: `http://localhost:3000` (service name `frontend` internally).
  - Use `docker-compose build --target development` for dev-specific builds.
- **Secrets**: Do **NOT** hardcode API keys. Use `.env.example` as a template and read from `.env`.

## Project Structure
- `config/`: Configuration files and sources.
- `parsers/`: Data fetching and parsing logic.
- `tasks/`: Project logs, todo lists, and lessons.
- `plan.md`: The current master plan. Always respect it.

## Coding Standards
- Follow the patterns in `main.py` and existing `parsers.py`.
- Write tests in `tests/` for new functionality.
