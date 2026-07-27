# Branch: feature/authentication

## Objective
Implement password hashing, JWT token generation/verification, and the
register/login/refresh flow.

## What's Implemented
- `app/core/security.py` — bcrypt password hashing (via passlib), JWT
  access/refresh token creation and decoding
- `app/core/exceptions.py` — domain-specific exceptions
  (EmailAlreadyExistsError, InvalidCredentialsError, InvalidTokenError)
- `app/schemas/user.py` — Pydantic schemas (UserCreate, UserLogin,
  UserRead, Token) — UserRead deliberately excludes password_hash
- `app/repositories/user_repository.py` — pure data access layer
- `app/services/auth_service.py` — register/login/refresh business logic
- `app/api/dependencies.py` — `get_current_user` dependency (decodes JWT
  from request, loads the user)
- `app/api/v1/auth.py` — POST /auth/register, /auth/login, /auth/refresh,
  GET /auth/me

## Key Design Decisions
- Two-token pattern: short-lived access token (30 min), long-lived
  refresh token (7 days)
- Login returns an identical error for "no such user" and "wrong
  password" — prevents email enumeration attacks
- `HTTPBearer` used instead of `OAuth2PasswordBearer` — our login accepts
  JSON (email/password), not OAuth2's form-encoded username/password grant
- Token payload never contains sensitive data (JWTs are signed, not
  encrypted — anyone can decode the payload)

## Verification
- Verified end-to-end via Postman: register (201), login (200 with
  tokens), authenticated /me (200), tampered token rejection (401)
