# app/core/exceptions.py
"""
Domain-specific exceptions. Services raise these; the API layer
(built later) catches them and translates to appropriate HTTP status
codes. Keeping exceptions here (not scattered per-module) gives one
place to see every distinct failure mode in the system.
"""


class DomainError(Exception):
    """Base class for all domain-level exceptions."""


class EmailAlreadyExistsError(DomainError):
    """Raised when registering with an email that's already in use."""


class InvalidCredentialsError(DomainError):
    """Raised on login when email/password don't match."""


class InvalidTokenError(DomainError):
    """Raised when a JWT is invalid, expired, or of the wrong type."""


class UserNotFoundError(DomainError):
    """Raised when a referenced user doesn't exist or is soft-deleted."""
