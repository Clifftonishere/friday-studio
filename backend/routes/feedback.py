"""Friday Studio — Asset approval/rejection routes."""

from __future__ import annotations

import asyncio
from typing import TypedDict

from fastapi import APIRouter, HTTPException

from backend.database import (
    get_db, get_asset, update_asset, create_feedback,
    check_stage_all_approved, get_stage, update_stage, update_project,
    get_assets,
)
from backend.models import FeedbackCreate
from backend.worker import run_stage, event_queues

router = APIRouter(tags=["feedback"])


TOTAL_STAGES = 6


class ApproveResponse(TypedDict):
    ok: bool
    status: str


class RejectResponse(TypedDict):
    ok: bool
    status: str
    comment: str | None


class OkResponse(TypedDict):
    ok: bool


def _get_stage_number_for_asset(asset_id: str) -> tuple[str, int]:
    """Return (project_id, stage_number) for an asset."""
    conn = get_db()
    row = conn.execute(
        "SELECT a.project_id, s.stage_number FROM assets a JOIN stages s ON a.stage_id = s.id WHERE a.id=?",
        (asset_id,),
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Asset not found")
    return row["project_id"], row["stage_number"]


async def _advance_after_stage_approved(project_id: str, stage_num: int) -> None:
    """Mark the stage approved, notify SSE, and kick off the next stage if any.

    Called from both the per-asset approve path and the bulk approve path
    after they've verified that all assets in the stage are approved.
    Assumes the stage has already been marked approved by the caller.
    """
    queue = event_queues.setdefault(project_id, asyncio.Queue())
    await queue.put({"type": "stage_approved", "data": {"stage": stage_num}})

    next_stage_num = stage_num + 1
    if next_stage_num <= TOTAL_STAGES:
        next_stage = get_stage(project_id, next_stage_num)
        if next_stage and next_stage["status"] == "pending":
            update_project(project_id, current_stage=next_stage_num)
            asyncio.create_task(run_stage(project_id, next_stage_num, queue))
    else:
        update_project(project_id, status="completed")


@router.post("/assets/{asset_id}/approve")
async def api_approve_asset(asset_id: str) -> ApproveResponse:
    asset = get_asset(asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")

    update_asset(asset_id, status="approved")
    create_feedback(asset_id, "approve")

    project_id, stage_num = _get_stage_number_for_asset(asset_id)

    if check_stage_all_approved(project_id, stage_num):
        stage = get_stage(project_id, stage_num)
        update_stage(stage["id"], status="approved")
        update_project(project_id, current_stage=stage_num)
        await _advance_after_stage_approved(project_id, stage_num)

    return {"ok": True, "status": "approved"}


@router.post("/assets/{asset_id}/reject")
async def api_reject_asset(asset_id: str, body: FeedbackCreate) -> RejectResponse:
    asset = get_asset(asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")

    update_asset(asset_id, status="rejected")
    create_feedback(asset_id, "reject", body.comment)

    return {"ok": True, "status": "rejected", "comment": body.comment}


@router.post("/projects/{project_id}/stages/{stage_num}/approve-all")
async def api_approve_all(project_id: str, stage_num: int) -> OkResponse:
    assets = get_assets(project_id, stage_number=stage_num)
    for asset in assets:
        if asset["status"] == "pending_review":
            update_asset(asset["id"], status="approved")
            create_feedback(asset["id"], "approve")

    if check_stage_all_approved(project_id, stage_num):
        stage = get_stage(project_id, stage_num)
        update_stage(stage["id"], status="approved")
        await _advance_after_stage_approved(project_id, stage_num)

    return {"ok": True}
