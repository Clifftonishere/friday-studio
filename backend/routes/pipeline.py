"""Friday Studio — Pipeline control routes."""

from __future__ import annotations

import asyncio
from typing import TypedDict

from fastapi import APIRouter, HTTPException

from backend.database import (
    get_project, get_uploads, create_stages, get_stage,
    update_project, get_assets, StageDict, AssetDict,
)
from backend.worker import run_stage, event_queues

router = APIRouter(tags=["pipeline"])


class PipelineStartResponse(TypedDict):
    ok: bool
    stages: list[StageDict]


class StageRunResponse(TypedDict):
    ok: bool
    stage: int


@router.post("/projects/{project_id}/start")
async def api_start_pipeline(project_id: str) -> PipelineStartResponse:
    project = get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project["status"] != "draft":
        raise HTTPException(400, f"Project is already {project['status']}")

    uploads = get_uploads(project_id)
    if not uploads:
        raise HTTPException(400, "No media uploaded")

    stages = create_stages(project_id)
    update_project(project_id, status="processing", current_stage=1)

    queue = event_queues.setdefault(project_id, asyncio.Queue())
    asyncio.create_task(run_stage(project_id, 1, queue))

    return PipelineStartResponse(ok=True, stages=stages)


@router.post("/projects/{project_id}/stages/{stage_num}/run")
async def api_run_stage(project_id: str, stage_num: int) -> StageRunResponse:
    """Manually trigger a specific stage (for re-runs)."""
    stage = get_stage(project_id, stage_num)
    if not stage:
        raise HTTPException(404, "Stage not found")

    queue = event_queues.setdefault(project_id, asyncio.Queue())
    asyncio.create_task(run_stage(project_id, stage_num, queue))

    return StageRunResponse(ok=True, stage=stage_num)


@router.get("/projects/{project_id}/stages")
def api_get_stages(project_id: str) -> list[StageDict]:
    project = get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project["stages"]


@router.get("/projects/{project_id}/stages/{stage_num}/assets")
def api_get_stage_assets(project_id: str, stage_num: int) -> list[AssetDict]:
    return get_assets(project_id, stage_number=stage_num)
