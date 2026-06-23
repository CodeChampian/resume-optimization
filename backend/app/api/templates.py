import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.db.mongodb import get_db
from app.core.config import settings
from app.models.template import ResumeTemplate, ResumeTemplateInDB, SUPPORTED_ROLES
from app.services.latex_service import latex_service

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("/upload", response_model=ResumeTemplate, status_code=201)
async def upload_template(
    project_id: str = Form(...),
    role: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ResumeTemplate:
    if role not in SUPPORTED_ROLES:
        raise HTTPException(status_code=400, detail=f"Unsupported role: {role}")

    if not file.filename or not file.filename.endswith(".tex"):
        raise HTTPException(status_code=400, detail="File must be a .tex file")

    content = await file.read()
    latex_content = content.decode("utf-8")

    os.makedirs(settings.templates_dir, exist_ok=True)
    file_path = os.path.join(settings.templates_dir, f"{role}.tex")
    with open(file_path, "w") as f:
        f.write(latex_content)

    existing = await db.resume_templates.find_one(
        {"project_id": ObjectId(project_id), "role": role}
    )

    doc = {
        "project_id": ObjectId(project_id),
        "role": role,
        "filename": file.filename,
        "latex_content": latex_content,
        "created_at": datetime.utcnow(),
    }

    if existing:
        await db.resume_templates.update_one(
            {"_id": existing["_id"]},
            {"$set": doc},
        )
        doc["_id"] = existing["_id"]
    else:
        result = await db.resume_templates.insert_one(doc)
        doc["_id"] = result.inserted_id

    return ResumeTemplateInDB(**doc).to_dto()


@router.get("", response_model=list[ResumeTemplate])
async def list_templates(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[ResumeTemplate]:
    cursor = db.resume_templates.find(
        {"project_id": ObjectId(project_id)}
    )
    templates = await cursor.to_list(length=100)
    return [ResumeTemplateInDB(**t).to_dto() for t in templates]


@router.get("/{template_id}/preview")
async def preview_template(
    template_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.resume_templates.find_one({"_id": ObjectId(template_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Template not found")

    pdf_filename = latex_service.compile(doc["latex_content"])
    if not pdf_filename:
        raise HTTPException(status_code=500, detail="Failed to compile PDF preview")

    pdf_path = os.path.join(settings.generated_dir, pdf_filename)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{doc['role']}_preview.pdf",
        headers={"Content-Disposition": "inline"},
    )
