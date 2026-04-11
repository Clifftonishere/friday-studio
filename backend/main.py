"""Friday Studio — FastAPI application."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.routes import projects, uploads, pipeline, feedback, sse

DATA_DIR = os.environ.get("FRIDAY_DATA_DIR", "/data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Friday Studio API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(sse.router, prefix="/api")

# Serve generated project files
projects_dir = Path(f"{DATA_DIR}/projects")
projects_dir.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(projects_dir)), name="project_files")
