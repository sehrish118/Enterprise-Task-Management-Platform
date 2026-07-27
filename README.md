# Branch: feature/authorization-rbac

## Objective
Implement Role-Based Access Control — permission checking scoped to
organization membership.

## What's Implemented
- `app/repositories/rbac_repository.py`:
  - `user_has_permission()` — single-query join across
    organization_members → roles → role_permissions → permissions
  - `is_organization_member()` — membership-only check
- `require_permission()` dependency factory in `app/api/dependencies.py`
  — declarative, per-endpoint permission checks
  (`Depends(require_permission(Permissions.TASK_CREATE))`)

## Key Design Decisions
- Organization context is taken from the URL path parameter
  (`/organizations/{organization_id}/...`) — explicit and unambiguous,
  since a user can belong to multiple organizations
- Permission check is a single database round-trip, not four separate
  queries — avoids N+1 query cost on every protected request
- 403 Forbidden (not 401) is returned when the user is authenticated but
  lacks permission — distinct from 401 (not authenticated at all)
- Soft-deleted organization memberships are excluded from every
  permission check

## Verification
- Verified end-to-end via Postman: allowed permission (200), denied
  permission (403), and non-member organization access (403)
