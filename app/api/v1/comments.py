import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.exceptions import CommentNotFoundError, NotCommentOwnerError
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.services.comment_service import CommentService

router = APIRouter(
    prefix="/organizations/{organization_id}/tasks/{task_id}/comments",
    tags=["comments"],
)


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: CommentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentRead:
    service = CommentService(db)
    comment = await service.create_comment(
        organization_id=organization_id,
        task_id=task_id,
        user_id=current_user.id,
        content=payload.content,
        parent_comment_id=payload.parent_comment_id,
    )
    return CommentRead.model_validate(comment)


@router.get("", response_model=list[CommentRead])
async def list_comments(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CommentRead]:
    service = CommentService(db)
    comments = await service.list_comments(task_id)
    return [CommentRead.model_validate(c) for c in comments]


@router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    comment_id: uuid.UUID,
    payload: CommentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentRead:
    service = CommentService(db)
    try:
        comment = await service.update_comment(
            comment_id=comment_id,
            requesting_user_id=current_user.id,
            content=payload.content,
        )
    except CommentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except NotCommentOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    return CommentRead.model_validate(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = CommentService(db)
    try:
        await service.delete_comment(
            comment_id=comment_id, requesting_user_id=current_user.id
        )
    except CommentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except NotCommentOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
