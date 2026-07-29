import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.exceptions import (
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyTeamMemberError,
    UserNotFoundError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.schemas.team import (
    AddTeamMemberRequest,
    TeamCreate,
    TeamMemberRead,
    TeamRead,
    TeamUpdate,
)
from app.services.team_service import TeamService

router = APIRouter(prefix="/organizations/{organization_id}/teams", tags=["teams"])


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    organization_id: uuid.UUID,
    payload: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_CREATE))],
) -> TeamRead:
    service = TeamService(db)
    try:
        team = await service.create_team(
            organization_id=organization_id, name=payload.name
        )
    except TeamNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return TeamRead.model_validate(team)


@router.get("", response_model=list[TeamRead])
async def list_teams(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TeamRead]:
    service = TeamService(db)
    teams = await service.list_teams(organization_id)
    return [TeamRead.model_validate(t) for t in teams]


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamRead:
    service = TeamService(db)
    try:
        team = await service.get_team(team_id)
    except TeamNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return TeamRead.model_validate(team)


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    payload: TeamUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
) -> TeamRead:
    service = TeamService(db)
    try:
        team = await service.update_team(team_id=team_id, name=payload.name)
    except TeamNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return TeamRead.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_DELETE))],
) -> None:
    service = TeamService(db)
    try:
        await service.delete_team(team_id)
    except TeamNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_team_member(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    payload: AddTeamMemberRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
) -> TeamMemberRead:
    service = TeamService(db)
    try:
        member = await service.add_member(
            organization_id=organization_id,
            team_id=team_id,
            email=payload.email,
            role=payload.role,
        )
    except TeamNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserAlreadyTeamMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    return TeamMemberRead.model_validate(member)


@router.get("/{team_id}/members", response_model=list[TeamMemberRead])
async def list_team_members(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TeamMemberRead]:
    service = TeamService(db)
    try:
        members = await service.list_members(team_id)
    except TeamNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return [TeamMemberRead.model_validate(m) for m in members]
