"""Friday Studio — Media upload routes."""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.database import (
    get_project, create_upload, update_upload_style,
    bulk_update_upload_style, delete_upload, set_soundtrack_config,
)
from backend.models import UploadStyleUpdate, BulkStyleUpdate, SoundtrackConfig

router = APIRouter(tags=["uploads"])
DATA_DIR = os.environ.get("FRIDAY_DATA_DIR", "/data")

ALLOWED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
ALLOWED_VIDEO_TYPES = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_AUDIO_TYPES = {".mp3", ".wav", ".aac", ".m4a", ".flac"}


def _classify_media(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_IMAGE_TYPES:
        return "photo"
    if ext in ALLOWED_VIDEO_TYPES:
        return "video"
    raise HTTPException(400, f"Unsupported file type: {ext}")


@router.post("/projects/{project_id}/uploads")
async def api_upload_media(
    project_id: str,
    file: UploadFile = File(...),
    style: str = Form("original"),
):
    project = get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if style not in ("original", "anime", "pixar"):
        raise HTTPException(400, "Style must be original, anime, or pixar")

    media_type = _classify_media(file.filename)
    upload_dir = Path(f"{DATA_DIR}/projects/{project_id}/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = str(upload_dir / safe_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    upload = create_upload(project_id, file.filename, file_path, media_type, style)
    upload["url"] = f"/files/{project_id}/uploads/{safe_name}"
    return upload


@router.patch("/projects/{project_id}/uploads/{upload_id}")
def api_update_upload_style(project_id: str, upload_id: str, body: UploadStyleUpdate):
    if body.style not in ("original", "anime", "pixar"):
        raise HTTPException(400, "Style must be original, anime, or pixar")
    update_upload_style(upload_id, body.style)
    return {"ok": True}


@router.patch("/projects/{project_id}/uploads/bulk-style")
def api_bulk_update_style(project_id: str, body: BulkStyleUpdate):
    if body.style not in ("original", "anime", "pixar"):
        raise HTTPException(400, "Style must be original, anime, or pixar")
    bulk_update_upload_style(project_id, body.style)
    return {"ok": True}


@router.delete("/projects/{project_id}/uploads/{upload_id}")
def api_delete_upload(project_id: str, upload_id: str):
    delete_upload(upload_id)
    return {"ok": True}


@router.post("/projects/{project_id}/soundtrack")
async def api_set_soundtrack(
    project_id: str,
    mode: str = Form(...),
    file: UploadFile | None = File(None),
):
    project = get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if mode not in ("upload", "ai_generate"):
        raise HTTPException(400, "Mode must be upload or ai_generate")

    uploaded_path = None
    if mode == "upload":
        if not file:
            raise HTTPException(400, "Audio file required when mode is upload")
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(400, f"Unsupported audio type: {ext}")
        audio_dir = Path(f"{DATA_DIR}/projects/{project_id}/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"soundtrack_{uuid.uuid4().hex[:8]}{ext}"
        uploaded_path = str(audio_dir / safe_name)
        with open(uploaded_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    set_soundtrack_config(project_id, mode, uploaded_path)
    return {"ok": True, "mode": mode}
