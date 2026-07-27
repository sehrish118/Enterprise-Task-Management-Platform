# app/services/auth_service.py
"""
Authentication business logic — register, login, token refresh.

This is where hashing utilities (core/security.py) and data access
(repositories/user_repository.py) come together. Routers will call
these methods; routers never talk to the repository or security.py
directly — that would leak business logic into the API layer.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, *, email: str, password: str, full_name: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyExistsError(f"Email '{email}' is already registered")

        password_hash = hash_password(password)
        user = await self.user_repo.create(
            email=email, password_hash=password_hash, full_name=full_name
        )
        await self.session.commit()
        return user

    async def login(self, *, email: str, password: str) -> tuple[str, str]:
        """Returns (access_token, refresh_token)."""
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            # Deliberately identical error for "no such user" and "wrong
            # password" — distinguishing them lets an attacker enumerate
            # valid emails.
            raise InvalidCredentialsError("Incorrect email or password")

        if not user.is_active:
            raise InvalidCredentialsError("Incorrect email or password")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return access_token, refresh_token

    async def refresh_access_token(self, *, refresh_token: str) -> str:
        try:
            user_id: uuid.UUID = decode_token(refresh_token, TokenType.REFRESH)
        except ValueError as e:
            raise InvalidTokenError(str(e)) from e

        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("User no longer exists or is inactive")

        return create_access_token(user.id)
