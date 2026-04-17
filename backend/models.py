"""Pydantic models for API request/response."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Nested response models
# ---------------------------------------------------------------------------

class UploadOut(BaseModel):
    id: str
    project_id: str
    filename: str
    file_path: str
    media_type: Literal["photo", "video"]
    style: Literal["original", "anime", "pixar"]
    sort_order: int
    created_at: str


class StageOut(BaseModel):
    id: str
    project_id: str
    stage_number: int
    stage_name: str
    status: Literal["pending", "running", "awaiting_review", "approved", "failed"]
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


class SoundtrackConfigOut(BaseModel):
    project_id: str
    mode: Literal["upload", "ai_generate"]
    uploaded_path: str | None = None


class AssetOut(BaseModel):
    id: str
    project_id: str
    stage_id: str
    asset_type: Literal["script", "character_sheet", "keyframe", "clip", "audio", "final_video"]
    file_path: str | None = None
    text_content: str | None = None
    metadata: str | None = None
    version: int
    status: Literal["pending_review", "approved", "rejected"]
    created_at: str


class FeedbackOut(BaseModel):
    id: str
    asset_id: str
    action: Literal["approve", "reject"]
    comment: str | None = None
    created_at: str


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    title: str
    brief: str


class ProjectOut(BaseModel):
    id: str
    title: str
    brief: str
    status: str
    current_stage: int
    created_at: str
    updated_at: str
    uploads: list[UploadOut] | None = None
    stages: list[StageOut] | None = None
    soundtrack: SoundtrackConfigOut | None = None


class UploadStyleUpdate(BaseModel):
    style: Literal["original", "anime", "pixar"]


class BulkStyleUpdate(BaseModel):
    style: Literal["original", "anime", "pixar"]


class SoundtrackConfig(BaseModel):
    mode: Literal["upload", "ai_generate"]


class FeedbackCreate(BaseModel):
    comment: str | None = None
