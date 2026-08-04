"""Web routes for projects — reuses ProjectService."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProjectNameAlreadyExistsError
from app.db.session import get_db
from app.models.user import User
from app.services.project_service import ProjectService
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter(tags=["web-projects"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/projects")
async def list_projects(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_uuid = uuid.UUID(organization_id)
    service = ProjectService(db)
    projects = await service.list_projects(org_uuid)
    return templates.TemplateResponse(
        request,
        "projects.html",
        {"projects": projects, "organization_id": organization_id},
    )


@router.post("/organizations/{organization_id}/projects")
async def create_project(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
):
    org_uuid = uuid.UUID(organization_id)
    service = ProjectService(db)
    try:
        await service.create_project(
            organization_id=org_uuid, name=name, created_by=current_user.id
        )
    except ProjectNameAlreadyExistsError:
        projects = await service.list_projects(org_uuid)
        return templates.TemplateResponse(
            request,
            "projects.html",
            {
                "projects": projects,
                "organization_id": organization_id,
                "error": "Project name already exists",
            },
        )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects", status_code=303
    )


@router.get("/organizations/{organization_id}/projects/{project_id}")
async def project_detail(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = ProjectService(db)
    project = await service.get_project(uuid.UUID(project_id))
    return templates.TemplateResponse(
        request, "project_detail.html", {"project": project}
    )
