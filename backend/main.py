"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.routes import projects, uploads, pipeline, feedback, sse

DATA_DIR = os.environ.get("FRIDAY_DATA_DIR", "/data")
FRONTEND_DIR = Path(os.environ.get("FRIDAY_FRONTEND_DIR", "/srv/frontend")).resolve()


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

# Generated project assets (character sheets, clips, audio, etc.)
projects_dir = Path(f"{DATA_DIR}/projects")
projects_dir.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(projects_dir)), name="project_files")


def _resolve_frontend_file(path: str) -> Path | None:
    """Map a request path to a file inside FRONTEND_DIR.

    Tries, in order:
      1. The path as-is (for assets like /favicon.ico, /_next/static/...)
      2. path.html (Next.js 16 static export emits flat new.html, project.html)
      3. path/index.html (standard directory-style fallback)

    Returns None if no match is found or if the resolved path escapes
    FRONTEND_DIR (path traversal protection).
    """
    if not FRONTEND_DIR.is_dir():
        return None

    clean = path.strip("/")
    candidates = [clean, f"{clean}.html", f"{clean}/index.html"] if clean else ["index.html"]

    for candidate in candidates:
        target = (FRONTEND_DIR / candidate).resolve()
        try:
            target.relative_to(FRONTEND_DIR)
        except ValueError:
            continue
        if target.is_file():
            return target

    return None


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str) -> FileResponse:
    file = _resolve_frontend_file(full_path)
    if file:
        return FileResponse(file)

    not_found = FRONTEND_DIR / "404.html"
    if not_found.is_file():
        return FileResponse(not_found, status_code=404)

    raise HTTPException(404)
