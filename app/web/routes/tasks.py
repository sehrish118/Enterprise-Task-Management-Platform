"""Web routes for tasks — reuses TaskService, TaskStatusService, CommentService."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TaskStatusNotFoundError,
    UserAlreadyAssignedError,
    UserNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.services.comment_service import CommentService
from app.services.task_service import TaskService
from app.services.task_status_service import TaskStatusService
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter(tags=["web-tasks"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/projects/{project_id}/tasks")
async def list_tasks(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task_service = TaskService(db)
    status_service = TaskStatusService(db)
    tasks, _ = await task_service.list_tasks(
        uuid.UUID(project_id), page=1, page_size=100
    )
    statuses = await status_service.list_statuses(uuid.UUID(organization_id))
    return templates.TemplateResponse(
        request,
        "tasks.html",
        {
            "tasks": tasks,
            "statuses": statuses,
            "organization_id": organization_id,
            "project_id": project_id,
        },
    )


@router.post("/organizations/{organization_id}/projects/{project_id}/tasks")
async def create_task(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form()],
    status_id: Annotated[str, Form()],
    priority: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
):
    task_service = TaskService(db)
    try:
        await task_service.create_task(
            organization_id=uuid.UUID(organization_id),
            project_id=uuid.UUID(project_id),
            status_id=uuid.UUID(status_id),
            title=title,
            description=description or None,
            priority=priority,
            parent_task_id=None,
            due_date=None,
            created_by=current_user.id,
        )
    except TaskStatusNotFoundError:
        pass  # form only offers valid statuses; this shouldn't normally trigger
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{project_id}/tasks",
        status_code=303,
    )


@router.get("/organizations/{organization_id}/projects/{project_id}/tasks/{task_id}")
async def task_detail(
    request: Request,
    organization_id: str,
    project_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task_service = TaskService(db)
    comment_service = CommentService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    assignees = await task_service.list_assignees(uuid.UUID(task_id))
    comments = await comment_service.list_comments(uuid.UUID(task_id))
    return templates.TemplateResponse(
        request,
        "task_detail.html",
        {
            "task": task,
            "assignees": assignees,
            "comments": comments,
            "organization_id": organization_id,
        },
    )


@router.post("/organizations/{organization_id}/tasks/{task_id}/assignees")
async def assign_task(
    request: Request,
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Form()],
):
    task_service = TaskService(db)
    try:
        await task_service.assign_user(
            organization_id=uuid.UUID(organization_id),
            task_id=uuid.UUID(task_id),
            email=email,
        )
    except (UserNotFoundError, UserAlreadyAssignedError):
        pass
    task = await task_service.get_task(uuid.UUID(task_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )


@router.post("/organizations/{organization_id}/tasks/{task_id}/comments")
async def add_comment(
    request: Request,
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    content: Annotated[str, Form()],
):
    comment_service = CommentService(db)
    await comment_service.create_comment(
        organization_id=uuid.UUID(organization_id),
        task_id=uuid.UUID(task_id),
        user_id=current_user.id,
        content=content,
        parent_comment_id=None,
    )
    task_service = TaskService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )
