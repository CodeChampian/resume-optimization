from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId


class OptimizationJob(BaseModel):
    id: str
    project_id: str
    status: str
    created_at: datetime


class OptimizationJobInDB(BaseModel):
    id: ObjectId = Field(alias="_id")
    project_id: ObjectId
    status: str
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}

    def to_dto(self) -> OptimizationJob:
        return OptimizationJob(
            id=str(self.id),
            project_id=str(self.project_id),
            status=self.status,
            created_at=self.created_at,
        )


class GeneratedResume(BaseModel):
    id: str
    job_id: str
    role: str
    jd_id: str
    jd_title: str
    company_name: str = ""
    ats_before: int | None = None
    ats_after: int | None = None
    optimized_latex: str | None = None
    pdf_path: str | None = None
    created_at: datetime


class GeneratedResumeInDB(BaseModel):
    id: ObjectId = Field(alias="_id")
    job_id: ObjectId
    role: str
    jd_id: ObjectId
    jd_title: str
    company_name: str = ""
    ats_before: int | None = None
    ats_after: int | None = None
    optimized_latex: str | None = None
    pdf_path: str | None = None
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}

    def to_dto(self) -> GeneratedResume:
        return GeneratedResume(
            id=str(self.id),
            job_id=str(self.job_id),
            role=self.role,
            jd_id=str(self.jd_id),
            jd_title=self.jd_title,
            company_name=self.company_name,
            ats_before=self.ats_before,
            ats_after=self.ats_after,
            optimized_latex=self.optimized_latex,
            pdf_path=self.pdf_path,
            created_at=self.created_at,
        )
