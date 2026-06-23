from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.db.mongodb import get_db
from app.models.project import ProjectCreate, Project, ProjectInDB

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=Project, status_code=201)
async def create_project(
    body: ProjectCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Project:
    doc = {
        "name": body.name,
        "created_at": datetime.utcnow(),
    }
    result = await db.projects.insert_one(doc)
    created = await db.projects.find_one({"_id": result.inserted_id})
    return ProjectInDB(**created).to_dto()


@router.get("", response_model=list[Project])
async def list_projects(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[Project]:
    cursor = db.projects.find().sort("created_at", -1)
    projects = await cursor.to_list(length=100)
    return [ProjectInDB(**p).to_dto() for p in projects]


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Project:
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectInDB(**project).to_dto()
