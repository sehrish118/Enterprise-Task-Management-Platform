import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.team_member import TeamMember, TeamMemberRole


class TeamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, team_id: uuid.UUID) -> Team | None:
        result = await self.session.execute(
            select(Team).where(Team.id == team_id, Team.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self, *, organization_id: uuid.UUID, name: str
    ) -> Team | None:
        result = await self.session.execute(
            select(Team).where(
                Team.organization_id == organization_id,
                Team.name == name,
                Team.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, *, organization_id: uuid.UUID, name: str) -> Team:
        team = Team(organization_id=organization_id, name=name)
        self.session.add(team)
        await self.session.flush()
        return team

    async def update(self, team: Team, *, name: str | None = None) -> Team:
        if name is not None:
            team.name = name
        await self.session.flush()
        return team

    async def soft_delete(self, team: Team) -> None:
        from datetime import datetime, timezone

        team.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Team]:
        result = await self.session.execute(
            select(Team).where(
                Team.organization_id == organization_id, Team.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())

    async def add_member(
        self,
        *,
        organization_id: uuid.UUID,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        role: TeamMemberRole,
    ) -> TeamMember:
        member = TeamMember(
            organization_id=organization_id, team_id=team_id, user_id=user_id, role=role
        )
        self.session.add(member)
        await self.session.flush()
        return member

    async def get_membership(
        self, *, team_id: uuid.UUID, user_id: uuid.UUID
    ) -> TeamMember | None:
        result = await self.session.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id, TeamMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_members(self, team_id: uuid.UUID) -> list[TeamMember]:
        result = await self.session.execute(
            select(TeamMember).where(TeamMember.team_id == team_id)
        )
        return list(result.scalars().all())
