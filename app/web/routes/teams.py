"""Web routes for teams — reuses TeamService."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TeamNameAlreadyExistsError
from app.db.session import get_db
from app.models.user import User
from app.services.team_service import TeamService
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter(tags=["web-teams"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/teams")
async def list_teams(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_uuid = uuid.UUID(organization_id)
    service = TeamService(db)
    teams = await service.list_teams(org_uuid)
    return templates.TemplateResponse(
        request, "teams.html", {"teams": teams, "organization_id": organization_id}
    )


@router.post("/organizations/{organization_id}/teams")
async def create_team(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
):
    org_uuid = uuid.UUID(organization_id)
    service = TeamService(db)
    try:
        await service.create_team(organization_id=org_uuid, name=name)
    except TeamNameAlreadyExistsError:
        teams = await service.list_teams(org_uuid)
        return templates.TemplateResponse(
            request,
            "teams.html",
            {
                "teams": teams,
                "organization_id": organization_id,
                "error": "Team name already exists",
            },
        )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/teams", status_code=303
    )
