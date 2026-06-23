from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import os
from app.db.mongodb import get_db
from app.core.config import settings
from app.models.optimization import GeneratedResume, GeneratedResumeInDB

router = APIRouter(prefix="/api/generated", tags=["generated"])


@router.get("", response_model=list[GeneratedResume])
async def list_generated(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[GeneratedResume]:
    job = await db.optimization_jobs.find_one(
        {"project_id": ObjectId(project_id)},
        sort=[("created_at", -1)],
    )
    if not job:
        return []

    cursor = db.generated_resumes.find(
        {"job_id": job["_id"]}
    ).sort("created_at", -1)
    results = await cursor.to_list(length=500)
    return [GeneratedResumeInDB(**r).to_dto() for r in results]


@router.get("/{generated_id}/download")
async def download_pdf(
    generated_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.generated_resumes.find_one(
        {"_id": ObjectId(generated_id)}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Generated resume not found")

    pdf_path = doc.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated yet")

    full_path = os.path.join(settings.generated_dir, pdf_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        full_path,
        media_type="application/pdf",
        filename=pdf_path,
    )
