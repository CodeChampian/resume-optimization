from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId


class JobDescription(BaseModel):
    id: str
    project_id: str
    role: str
    company_name: str = ""
    title: str
    content: str
    created_at: datetime


class JobDescriptionCreate(BaseModel):
    project_id: str
    role: str
    company_name: str = ""
    content: str


class BulkJDItem(BaseModel):
    company_name: str = ""
    content: str


class JDBulkCreate(BaseModel):
    project_id: str
    role: str
    items: list[BulkJDItem]


class JobDescriptionInDB(BaseModel):
    id: ObjectId = Field(alias="_id")
    project_id: ObjectId
    role: str
    company_name: str = ""
    title: str
    content: str
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}

    def to_dto(self) -> JobDescription:
        return JobDescription(
            id=str(self.id),
            project_id=str(self.project_id),
            role=self.role,
            company_name=self.company_name,
            title=self.title,
            content=self.content,
            created_at=self.created_at,
        )
