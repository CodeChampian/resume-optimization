from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId


class Project(BaseModel):
    id: str
    name: str
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str


class ProjectInDB(BaseModel):
    id: ObjectId = Field(alias="_id")
    name: str
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}

    def to_dto(self) -> Project:
        return Project(
            id=str(self.id),
            name=self.name,
            created_at=self.created_at,
        )
