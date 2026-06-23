from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import mongodb
from app.api import projects, templates, jds, optimize, generated


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    yield
    await mongodb.close()


app = FastAPI(title="Resume Optimizer API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(templates.router)
app.include_router(jds.router)
app.include_router(optimize.router)
app.include_router(generated.router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
