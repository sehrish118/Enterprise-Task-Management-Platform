import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    status: str | None = Field(
        default=None, description="ACTIVE, ON_HOLD, COMPLETED, ARCHIVED"
    )
    is_archived: bool | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    status: str
    is_archived: bool
    created_by: uuid.UUID
    created_at: datetime


class AddProjectMemberRequest(BaseModel):
    email: str
    role: str = Field(default="MEMBER", description="MEMBER or PROJECT_MANAGER")


class ProjectMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    role: str
