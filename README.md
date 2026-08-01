# ETMP — Enterprise Task Management Platform

A production-grade, multi-tenant SaaS backend for organization-based task
and project management. Built as a flagship backend engineering portfolio
project, following Clean Architecture principles end-to-end.

## Tech Stack

- **Framework:** FastAPI (fully async)
- **Database:** PostgreSQL + SQLAlchemy 2.0 (async, via asyncpg)
- **Migrations:** Alembic (async-compatible)
- **Validation:** Pydantic v2
- **Auth:** JWT (access + refresh tokens), bcrypt password hashing
- **Authorization:** Custom RBAC (Role-Based Access Control)
- **Testing:** Pytest (planned)
- **Infra:** Docker (planned)

## Architecture

Strict layered architecture with a one-directional dependency flow:

API (routers) → Services (business logic) → Repositories (data access) → Models (ORM)


- **Routers** — thin, HTTP concerns only, no business logic
- **Services** — all business logic, raises domain-specific exceptions
- **Repositories** — pure data access, no business logic, never commits
  transactions (that's the Service's responsibility)
- **Models** — SQLAlchemy ORM, no business logic

Never: business logic in routers, raw SQL in routers, ORM models coupled
to business logic, hardcoded configuration.

## Multi-Tenancy

Every tenant-scoped table carries a denormalized `organization_id`
column (not just derived through joins) — enables efficient tenant
isolation and is a prerequisite for future row-level security. See
`feature/database-setup` branch README for full schema rationale.

## Project Structure

app/
├── api/ # Routers + shared dependencies (auth, RBAC)
├── core/ # Config, security, logging, exceptions
├── db/ # Session management, declarative base, seed data
├── models/ # SQLAlchemy ORM models (18 tables)
├── schemas/ # Pydantic request/response schemas
├── repositories/ # Data access layer
├── services/ # Business logic layer
├── middleware/ # Custom middleware (planned)
├── utils/ # Pure, stateless helpers
├── enums/ # Shared enums and permission constants
└── tests/ # Automated test suite (planned)
alembic/ # Database migrations


## Branch Overview

This project follows a strict one-feature-per-branch workflow, merged
into `main` once each is verified end-to-end.

| Branch | Status | What It Adds |
|---|---|---|
| `feature/project-setup` | ✅ Merged | Project skeleton, config, logging |
| `feature/database-setup` | ✅ Merged | Async DB connection, all 18 models, Alembic migrations, RBAC seed data |
| `feature/authentication` | ✅ Merged | JWT auth, password hashing, register/login/refresh |
| `feature/authorization-rbac` | ✅ Merged | Role-based permission checking |
| `feature/user-module` | ✅ Merged | Profile management, password change, org-scoped user listing, deactivation |
| `feature/organization-module` | ✅ Merged | Organization CRUD, atomic owner creation, member invitations |
| `feature/team-module` | ✅ Merged | Team CRUD, member management, 
RBAC-gated |
| `feature/project-module` | ✅ Merged | Project CRUD, project members |
| `feature/task-module` | ✅ Merged | Task statuses, task CRUD, task assignment |
| `feature/comments-attachments` | ✅ Merged | Threaded comments (ownership-guarded edit/delete), attachment metadata |
| `feature/notifications-activity-logs` | ✅ Merged | Auto-triggered notifications, org-wide activity audit trail |
| `feature/search-filtering-pagination` | ✅ Merged | Search, filtering, pagination on task listing |
| `feature/dashboard-apis` | ✅ Merged | Personal dashboard (assigned/overdue tasks, notifications), organization dashboard (project/task/member stats) |
| `feature/middleware-exception-handling` | ✅ Merged | Request logging middleware, in-memory rate limiting |
| `feature/global-exception-handling` | 🚧 Next | Centralized DomainError → HTTP status code mapping |

Each branch has its own README (on that branch) with full implementation
details, design decisions, and verification notes for that specific step.

## Local Setup

```bash
cp .env.example .env   # then fill in real values
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements-dev.txt
python -m app.db.seed       # seed RBAC permissions/roles
alembic upgrade head        # apply migrations
uvicorn app.main:app --reload
```

API docs available at: `http://127.0.0.1:8000/api/v1/docs`

Requires a running local PostgreSQL instance matching `DATABASE_URL` in
`.env`. Dockerized setup is planned for a later stage.

## Roadmap

Project Setup → Git Strategy → Environment Config → Logging →
Database Connection → Alembic → **Authentication** → **Authorization (RBAC)**
→ **User Module** → *Organization Module* → Team Module → Project Module →
Task Module → Comments → Attachments → Notifications → Activity Logs →
Search/Filtering/Pagination → Dashboard APIs → Middleware/Exception
Handling → Testing → Docker → Production Optimization → Deployment