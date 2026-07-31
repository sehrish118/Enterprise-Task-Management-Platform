import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ProjectNameAlreadyExistsError,
    ProjectNotFoundError,
    UserAlreadyProjectMemberError,
    UserNotFoundError,
)
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)

    async def create_project(
        self, *, organization_id: uuid.UUID, name: str, created_by: uuid.UUID
    ) -> Project:
        existing = await self.project_repo.get_by_name(
            organization_id=organization_id, name=name
        )
        if existing is not None:
            raise ProjectNameAlreadyExistsError(
                f"Project '{name}' already exists in this organization"
            )
        project = await self.project_repo.create(
            organization_id=organization_id, name=name, created_by=created_by
        )
        # Creator is automatically added as a project member with elevated role
        await self.project_repo.add_member(
            organization_id=organization_id,
            project_id=project.id,
            user_id=created_by,
            role=ProjectMemberRole.PROJECT_MANAGER,
        )
        await self.session.commit()
        return project

    async def get_project(self, project_id: uuid.UUID) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        return project

    async def update_project(
        self,
        *,
        project_id: uuid.UUID,
        name: str | None,
        status: str | None,
        is_archived: bool | None,
    ) -> Project:
        project = await self.get_project(project_id)
        project = await self.project_repo.update(
            project, name=name, status=status, is_archived=is_archived
        )
        await self.session.commit()
        return project

    async def delete_project(self, project_id: uuid.UUID) -> None:
        project = await self.get_project(project_id)
        await self.project_repo.soft_delete(project)
        await self.session.commit()

    async def list_projects(self, organization_id: uuid.UUID) -> list[Project]:
        return await self.project_repo.list_by_organization(organization_id)

    async def add_member(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        email: str,
        role: str,
    ) -> ProjectMember:
        await self.get_project(project_id)

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UserNotFoundError(f"No user registered with email '{email}'")

        existing = await self.project_repo.get_membership(
            project_id=project_id, user_id=user.id
        )
        if existing is not None:
            raise UserAlreadyProjectMemberError(
                f"'{email}' is already a member of this project"
            )

        member = await self.project_repo.add_member(
            organization_id=organization_id,
            project_id=project_id,
            user_id=user.id,
            role=ProjectMemberRole(role),
        )
        await self.session.commit()
        return member

    async def list_members(self, project_id: uuid.UUID) -> list[ProjectMember]:
        await self.get_project(project_id)
        return await self.project_repo.list_members(project_id)
