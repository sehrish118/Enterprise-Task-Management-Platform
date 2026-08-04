"""Web-specific auth dependency — reads JWT from cookie instead of
Authorization header (browsers can't easily attach custom headers
from plain HTML/forms)."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def get_current_user_from_cookie(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    try:
        user_id = decode_token(access_token, TokenType.ACCESS)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    return user
