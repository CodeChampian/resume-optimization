from fastapi import APIRouter, BackgroundTasks, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import BaseModel
from app.db.mongodb import get_db
from app.services.optimization_service import optimization_service

router = APIRouter(prefix="/api/optimize", tags=["optimize"])


class OptimizeRequest(BaseModel):
    project_id: str


@router.post("", status_code=202)
async def start_optimization(
    body: OptimizeRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    background_tasks.add_task(optimization_service.run, body.project_id)
    return {
        "message": "Optimization started",
        "project_id": body.project_id,
    }


@router.get("/{project_id}/status")
async def get_optimization_status(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    job = await db.optimization_jobs.find_one(
        {"project_id": ObjectId(project_id)},
        sort=[("created_at", -1)],
    )
    if not job:
        return {"status": None}

    return {"status": job["status"]}
