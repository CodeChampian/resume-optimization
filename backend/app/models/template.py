from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

SUPPORTED_ROLES = [
    "business_analyst",
    "business_intelligence_analyst",
    "project_manager",
    "product_owner",
]


class ResumeTemplate(BaseModel):
    id: str
    project_id: str
    role: str
    filename: str
    latex_content: str
    created_at: datetime


class ResumeTemplateInDB(BaseModel):
    id: ObjectId = Field(alias="_id")
    project_id: ObjectId
    role: str
    filename: str
    latex_content: str
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}

    def to_dto(self) -> ResumeTemplate:
        return ResumeTemplate(
            id=str(self.id),
            project_id=str(self.project_id),
            role=self.role,
            filename=self.filename,
            latex_content=self.latex_content,
            created_at=self.created_at,
        )
