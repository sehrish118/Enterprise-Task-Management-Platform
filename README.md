# Branch: feature/database-setup

## Objective
Implement the full database layer: async SQLAlchemy connection, all 18
models from the frozen schema, and Alembic migrations.

## What's Implemented
- `app/db/session.py` — async engine (asyncpg driver) with connection
  pooling, `expire_on_commit=False` (required for async), and a `get_db()`
  FastAPI dependency with automatic rollback on exception
- `app/db/base.py` — SQLAlchemy declarative Base
- `app/models/` — all 18 tables as SQLAlchemy 2.0 models:
  users, organizations, organization_members, roles, permissions,
  role_permissions, teams, team_members, projects, project_members,
  task_statuses, tasks, task_assignees, comments, attachments,
  notification_types, notifications, activity_logs
- `alembic/env.py` — configured for async engine (bridges Alembic's sync
  migration runner via `run_sync()`), plus `CREATE EXTENSION citext`
  wired into the initial migration
- `app/enums/permissions.py` — centralized permission code registry
- `app/db/seed.py` — idempotent seed script for RBAC permissions and
  default system roles (Owner, Admin, Member)

## Key Design Decisions
- Multi-tenancy enforced via denormalized `organization_id` on every
  tenant-scoped table (not just derived through joins)
- Explicit FK cascade rules per relationship (RESTRICT for audit-critical
  references like task creator/status, CASCADE for org-owned data,
  SET NULL for optional parent-task links)
- `email` uses CITEXT for case-insensitive uniqueness at the DB level
- `notification_types` is a lookup table instead of a native Postgres
  ENUM — avoids costly ALTER TYPE operations as the system grows
- Central model registry (`app/models/__init__.py`) ensures all models
  register on `Base.metadata` when imported

## Verification
- `configure_mappers()` sanity check — all relationships wired correctly
- Migration applied successfully to local PostgreSQL (`alembic current`
  confirms head revision)
