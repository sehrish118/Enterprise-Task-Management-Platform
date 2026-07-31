import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.core.exceptions import (
    ProjectNameAlreadyExistsError,
    ProjectNotFoundError,
    UserAlreadyProjectMemberError,
    UserNotFoundError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.project import (
    AddProjectMemberRequest,
    ProjectCreate,
    ProjectMemberRead,
    ProjectRead,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/organizations/{organization_id}/projects", tags=["projects"]
)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    organization_id: uuid.UUID,
    payload: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_CREATE))],
) -> ProjectRead:
    service = ProjectService(db)
    try:
        project = await service.create_project(
            organization_id=organization_id,
            name=payload.name,
            created_by=current_user.id,
        )
    except ProjectNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return ProjectRead.model_validate(project)


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProjectRead]:
    service = ProjectService(db)
    projects = await service.list_projects(organization_id)
    return [ProjectRead.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectRead:
    service = ProjectService(db)
    try:
        project = await service.get_project(project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
) -> ProjectRead:
    service = ProjectService(db)
    try:
        project = await service.update_project(
            project_id=project_id,
            name=payload.name,
            status=payload.status,
            is_archived=payload.is_archived,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_DELETE))],
) -> None:
    service = ProjectService(db)
    try:
        await service.delete_project(project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: AddProjectMemberRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
) -> ProjectMemberRead:
    service = ProjectService(db)
    try:
        member = await service.add_member(
            organization_id=organization_id,
            project_id=project_id,
            email=payload.email,
            role=payload.role,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserAlreadyProjectMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    return ProjectMemberRead.model_validate(member)


@router.get("/{project_id}/members", response_model=list[ProjectMemberRead])
async def list_project_members(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProjectMemberRead]:
    service = ProjectService(db)
    try:
        members = await service.list_members(project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return [ProjectMemberRead.model_validate(m) for m in members]
