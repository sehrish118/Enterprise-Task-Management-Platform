import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, comment_id: uuid.UUID) -> Comment | None:
        result = await self.session.execute(
            select(Comment).where(
                Comment.id == comment_id, Comment.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
        parent_comment_id: uuid.UUID | None,
    ) -> Comment:
        comment = Comment(
            organization_id=organization_id,
            task_id=task_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def update(self, comment: Comment, *, content: str) -> Comment:
        comment.content = content
        comment.edited_at = datetime.now(timezone.utc)
        await self.session.flush()
        return comment

    async def soft_delete(self, comment: Comment) -> None:
        comment.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def list_by_task(self, task_id: uuid.UUID) -> list[Comment]:
        result = await self.session.execute(
            select(Comment)
            .where(Comment.task_id == task_id, Comment.deleted_at.is_(None))
            .order_by(Comment.created_at)
        )
        return list(result.scalars().all())
