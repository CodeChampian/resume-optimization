from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.db.mongodb import get_db
from app.models.jd import (
    JobDescription,
    JobDescriptionCreate,
    JDBulkCreate,
    BulkJDItem,
    JobDescriptionInDB,
)

router = APIRouter(prefix="/api/jds", tags=["job_descriptions"])


@router.post("", response_model=JobDescription, status_code=201)
async def add_jd(
    body: JobDescriptionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> JobDescription:
    project = await db.projects.find_one({"_id": ObjectId(body.project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc = {
        "project_id": ObjectId(body.project_id),
        "role": body.role,
        "company_name": body.company_name,
        "title": body.company_name,
        "content": body.content,
        "created_at": datetime.utcnow(),
    }
    result = await db.job_descriptions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return JobDescriptionInDB(**doc).to_dto()


@router.post("/bulk", status_code=201)
async def bulk_add_jds(
    body: JDBulkCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    project = await db.projects.find_one({"_id": ObjectId(body.project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    docs = [
        {
            "project_id": ObjectId(body.project_id),
            "role": body.role,
            "company_name": item.company_name,
            "title": item.company_name,
            "content": item.content,
            "created_at": datetime.utcnow(),
        }
        for item in body.items
    ]

    if docs:
        await db.job_descriptions.insert_many(docs)

    return {"created": len(docs)}


@router.get("", response_model=list[JobDescription])
async def list_jds(
    project_id: str,
    role: str | None = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[JobDescription]:
    query: dict = {"project_id": ObjectId(project_id)}
    if role:
        query["role"] = role

    cursor = db.job_descriptions.find(query).sort("created_at", -1)
    jds = await cursor.to_list(length=500)
    return [JobDescriptionInDB(**j).to_dto() for j in jds]


@router.delete("/{jd_id}", status_code=204)
async def delete_jd(
    jd_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> None:
    result = await db.job_descriptions.delete_one({"_id": ObjectId(jd_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="JD not found")
