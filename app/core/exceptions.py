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


class OrganizationNotFoundError(DomainError):
    """Raised when a referenced organization doesn't exist or is soft-deleted."""


class SlugAlreadyExistsError(DomainError):
    """Raised when creating an organization with a slug that's already taken."""


class RoleNotFoundError(DomainError):
    """Raised when a role name doesn't match any known role."""


class UserAlreadyMemberError(DomainError):
    """Raised when adding a user to an organization they're already part of."""


class TeamNotFoundError(DomainError):
    """Raised when a referenced team doesn't exist or is soft-deleted."""


class TeamNameAlreadyExistsError(DomainError):
    """Raised when creating a team with a name already used in the org."""


class UserAlreadyTeamMemberError(DomainError):
    """Raised when adding a user to a team they're already part of."""


class ProjectNotFoundError(DomainError):
    """Raised when a referenced project doesn't exist or is soft-deleted."""


class ProjectNameAlreadyExistsError(DomainError):
    """Raised when creating a project with a name already used in the org."""


class UserAlreadyProjectMemberError(DomainError):
    """Raised when adding a user to a project they're already part of."""


class TaskNotFoundError(DomainError):
    """Raised when a referenced task doesn't exist or is soft-deleted."""


class TaskStatusNotFoundError(DomainError):
    """Raised when a referenced task status doesn't exist."""


class TaskStatusAlreadyExistsError(DomainError):
    """Raised when creating a task status with a name already used in the org."""


class UserAlreadyAssignedError(DomainError):
    """Raised when assigning a user to a task they're already assigned to."""


class CommentNotFoundError(DomainError):
    """Raised when a referenced comment doesn't exist or is soft-deleted."""


class NotCommentOwnerError(DomainError):
    """Raised when a user tries to edit/delete another user's comment."""


class AttachmentNotFoundError(DomainError):
    """Raised when a referenced attachment doesn't exist or is soft-deleted."""
