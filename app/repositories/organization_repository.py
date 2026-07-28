"""Organization data access layer — pure DB queries, no business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.role import Role


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(
                Organization.id == organization_id, Organization.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(
                Organization.slug == slug, Organization.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def create(self, *, name: str, slug: str) -> Organization:
        org = Organization(name=name, slug=slug)
        self.session.add(org)
        await self.session.flush()
        return org

    async def update(
        self, org: Organization, *, name: str | None = None
    ) -> Organization:
        if name is not None:
            org.name = name
        await self.session.flush()
        return org

    async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(
                OrganizationMember,
                OrganizationMember.organization_id == Organization.id,
            )
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
                Organization.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_role_by_name(
        self, *, organization_id: uuid.UUID, role_name: str
    ) -> Role | None:
        """
        Looks up a role by name — checks org-scoped custom roles first,
        falls back to global system roles (Owner/Admin/Member).
        """
        result = await self.session.execute(
            select(Role).where(
                Role.name == role_name,
                (Role.organization_id == organization_id)
                | (Role.organization_id.is_(None)),
            )
        )
        return result.scalar_one_or_none()

    async def add_member(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID
    ) -> OrganizationMember:
        membership = OrganizationMember(
            organization_id=organization_id, user_id=user_id, role_id=role_id
        )
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def get_membership(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMember | None:
        result = await self.session.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
