"""Friday Studio — Pydantic models for API request/response."""

from pydantic import BaseModel


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
    uploads: list[dict] | None = None
    stages: list[dict] | None = None
    soundtrack: dict | None = None


class UploadStyleUpdate(BaseModel):
    style: str  # original | anime | pixar


class BulkStyleUpdate(BaseModel):
    style: str


class SoundtrackConfig(BaseModel):
    mode: str  # upload | ai_generate


class FeedbackCreate(BaseModel):
    comment: str | None = None
