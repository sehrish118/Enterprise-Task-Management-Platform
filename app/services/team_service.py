import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyTeamMemberError,
    UserNotFoundError,
)
from app.models.team import Team
from app.models.team_member import TeamMember, TeamMemberRole
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.team_repo = TeamRepository(session)
        self.user_repo = UserRepository(session)

    async def create_team(self, *, organization_id: uuid.UUID, name: str) -> Team:
        existing = await self.team_repo.get_by_name(
            organization_id=organization_id, name=name
        )
        if existing is not None:
            raise TeamNameAlreadyExistsError(
                f"Team '{name}' already exists in this organization"
            )
        team = await self.team_repo.create(organization_id=organization_id, name=name)
        await self.session.commit()
        return team

    async def get_team(self, team_id: uuid.UUID) -> Team:
        team = await self.team_repo.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(f"Team {team_id} not found")
        return team

    async def update_team(self, *, team_id: uuid.UUID, name: str | None) -> Team:
        team = await self.get_team(team_id)
        team = await self.team_repo.update(team, name=name)
        await self.session.commit()
        return team

    async def delete_team(self, team_id: uuid.UUID) -> None:
        team = await self.get_team(team_id)
        await self.team_repo.soft_delete(team)
        await self.session.commit()

    async def list_teams(self, organization_id: uuid.UUID) -> list[Team]:
        return await self.team_repo.list_by_organization(organization_id)

    async def add_member(
        self, *, organization_id: uuid.UUID, team_id: uuid.UUID, email: str, role: str
    ) -> TeamMember:
        await self.get_team(team_id)  # raises TeamNotFoundError if missing

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UserNotFoundError(f"No user registered with email '{email}'")

        existing = await self.team_repo.get_membership(team_id=team_id, user_id=user.id)
        if existing is not None:
            raise UserAlreadyTeamMemberError(
                f"'{email}' is already a member of this team"
            )

        member = await self.team_repo.add_member(
            organization_id=organization_id,
            team_id=team_id,
            user_id=user.id,
            role=TeamMemberRole(role),
        )
        await self.session.commit()
        return member

    async def list_members(self, team_id: uuid.UUID) -> list[TeamMember]:
        await self.get_team(team_id)
        return await self.team_repo.list_members(team_id)
