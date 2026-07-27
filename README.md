# Branch: feature/project-setup

## Objective
Establish the foundational project skeleton — directory structure, configuration
management, and logging — before any business logic is written.

## What's Implemented
- Frozen directory structure (api, core, db, models, schemas, repositories,
  services, middleware, utils, enums, tests)
- `app/core/config.py` — typed settings loader using pydantic-settings, reads
  from `.env`, includes production-safety validation (rejects insecure default
  secrets and DEBUG=true when APP_ENV=production)
- `app/core/logging.py` — structured logging: human-readable format in
  development, JSON format in production (log-aggregator ready)
- `app/main.py` — minimal FastAPI app factory with a `/health` endpoint
- `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` — dependency
  management with dev tools (pytest, ruff, mypy) kept separate from
  production dependencies
- `.gitignore`, `.env.example` — secrets excluded from version control

## Key Design Decisions
- Async stack chosen from the start (FastAPI is async-first)
- Config validation fails fast at startup rather than failing silently
  in production
- `main.py` deliberately kept thin — no business logic, no DB access
