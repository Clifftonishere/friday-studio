"""SQLite database layer."""

from __future__ import annotations

import sqlite3
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict


# ---------------------------------------------------------------------------
# TypedDicts — mirror the sqlite3.Row shapes returned by queries
# ---------------------------------------------------------------------------

class ProjectDict(TypedDict):
    id: str
    title: str
    brief: str
    status: str
    current_stage: int
    created_at: str
    updated_at: str


class ProjectDetailDict(ProjectDict):
    uploads: list[UploadDict]
    stages: list[StageDict]
    soundtrack: SoundtrackConfigDict | None


class UploadDict(TypedDict):
    id: str
    project_id: str
    filename: str
    file_path: str
    media_type: str
    style: str
    sort_order: int
    created_at: str


class StageDict(TypedDict):
    id: str
    project_id: str
    stage_number: int
    stage_name: str
    status: str
    started_at: str | None
    completed_at: str | None
    error_message: str | None


class AssetDict(TypedDict):
    id: str
    project_id: str
    stage_id: str
    asset_type: str
    file_path: str | None
    text_content: str | None
    metadata: str | None
    version: int
    status: str
    created_at: str


class FeedbackDict(TypedDict):
    id: str
    asset_id: str
    action: str
    comment: str | None
    created_at: str


class SoundtrackConfigDict(TypedDict):
    project_id: str
    mode: str
    uploaded_path: str | None

DB_PATH = "/data/friday.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            brief TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            current_stage INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS uploads (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            media_type TEXT NOT NULL,
            style TEXT NOT NULL DEFAULT 'original',
            sort_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stages (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            stage_number INTEGER NOT NULL,
            stage_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            started_at TEXT,
            completed_at TEXT,
            error_message TEXT,
            UNIQUE(project_id, stage_number)
        );

        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            stage_id TEXT NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
            asset_type TEXT NOT NULL,
            file_path TEXT,
            text_content TEXT,
            metadata TEXT,
            version INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending_review',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
            action TEXT NOT NULL,
            comment TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS soundtrack_config (
            project_id TEXT PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE,
            mode TEXT NOT NULL,
            uploaded_path TEXT
        );
    """)
    conn.commit()
    conn.close()


STAGE_NAMES = {
    1: "Script Writing",
    2: "Character Design",
    3: "Scene Composition",
    4: "Clip Animation",
    5: "Music Generation",
    6: "Final Assembly",
}


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def create_project(title: str, brief: str) -> ProjectDict:
    conn = get_db()
    project_id = _uuid()
    now = _now()
    conn.execute(
        "INSERT INTO projects (id, title, brief, status, current_stage, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        (project_id, title, brief, "draft", 0, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    return dict(row)


def list_projects() -> list[ProjectDict]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(project_id: str) -> ProjectDetailDict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not row:
        conn.close()
        return None
    project = dict(row)
    project["uploads"] = [dict(r) for r in conn.execute("SELECT * FROM uploads WHERE project_id=? ORDER BY sort_order", (project_id,)).fetchall()]
    project["stages"] = [dict(r) for r in conn.execute("SELECT * FROM stages WHERE project_id=? ORDER BY stage_number", (project_id,)).fetchall()]
    project["soundtrack"] = None
    sc = conn.execute("SELECT * FROM soundtrack_config WHERE project_id=?", (project_id,)).fetchone()
    if sc:
        project["soundtrack"] = dict(sc)
    conn.close()
    return project


def update_project(project_id: str, **kwargs: Any) -> None:
    conn = get_db()
    kwargs["updated_at"] = _now()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [project_id]
    conn.execute(f"UPDATE projects SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------

def create_upload(project_id: str, filename: str, file_path: str, media_type: str, style: str = "original") -> UploadDict:
    conn = get_db()
    upload_id = _uuid()
    max_order = conn.execute("SELECT COALESCE(MAX(sort_order),0) FROM uploads WHERE project_id=?", (project_id,)).fetchone()[0]
    conn.execute(
        "INSERT INTO uploads (id, project_id, filename, file_path, media_type, style, sort_order, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (upload_id, project_id, filename, file_path, media_type, style, max_order + 1, _now()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM uploads WHERE id=?", (upload_id,)).fetchone()
    conn.close()
    return dict(row)


def update_upload_style(upload_id: str, style: str) -> None:
    conn = get_db()
    conn.execute("UPDATE uploads SET style=? WHERE id=?", (style, upload_id))
    conn.commit()
    conn.close()


def bulk_update_upload_style(project_id: str, style: str) -> None:
    conn = get_db()
    conn.execute("UPDATE uploads SET style=? WHERE project_id=?", (style, project_id))
    conn.commit()
    conn.close()


def delete_upload(upload_id: str) -> None:
    conn = get_db()
    conn.execute("DELETE FROM uploads WHERE id=?", (upload_id,))
    conn.commit()
    conn.close()


def get_uploads(project_id: str, media_type: str | None = None) -> list[UploadDict]:
    conn = get_db()
    if media_type:
        rows = conn.execute("SELECT * FROM uploads WHERE project_id=? AND media_type=? ORDER BY sort_order", (project_id, media_type)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM uploads WHERE project_id=? ORDER BY sort_order", (project_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

def create_stages(project_id: str) -> list[StageDict]:
    conn = get_db()
    stages = []
    for num, name in STAGE_NAMES.items():
        stage_id = _uuid()
        conn.execute(
            "INSERT INTO stages (id, project_id, stage_number, stage_name, status) VALUES (?,?,?,?,?)",
            (stage_id, project_id, num, name, "pending"),
        )
        stages.append({"id": stage_id, "project_id": project_id, "stage_number": num, "stage_name": name, "status": "pending"})
    conn.commit()
    conn.close()
    return stages


def get_stage(project_id: str, stage_number: int) -> StageDict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM stages WHERE project_id=? AND stage_number=?", (project_id, stage_number)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_stage(stage_id: str, **kwargs: Any) -> None:
    conn = get_db()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [stage_id]
    conn.execute(f"UPDATE stages SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def create_asset(project_id: str, stage_id: str, asset_type: str, file_path: str | None = None, text_content: str | None = None, metadata: dict[str, Any] | None = None) -> AssetDict:
    conn = get_db()
    asset_id = _uuid()
    meta_json = json.dumps(metadata) if metadata else None
    conn.execute(
        "INSERT INTO assets (id, project_id, stage_id, asset_type, file_path, text_content, metadata, version, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (asset_id, project_id, stage_id, asset_type, file_path, text_content, meta_json, 1, "pending_review", _now()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    conn.close()
    return dict(row)


def get_assets(project_id: str, stage_number: int | None = None, asset_type: str | None = None, status: str | None = None) -> list[AssetDict]:
    conn = get_db()
    query = "SELECT a.* FROM assets a JOIN stages s ON a.stage_id = s.id WHERE a.project_id=?"
    params: list[Any] = [project_id]
    if stage_number is not None:
        query += " AND s.stage_number=?"
        params.append(stage_number)
    if asset_type:
        query += " AND a.asset_type=?"
        params.append(asset_type)
    if status:
        query += " AND a.status=?"
        params.append(status)
    query += " ORDER BY a.created_at"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_asset(asset_id: str) -> AssetDict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_asset(asset_id: str, **kwargs: Any) -> None:
    conn = get_db()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [asset_id]
    conn.execute(f"UPDATE assets SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def get_latest_asset_version(project_id: str, stage_id: str, asset_type: str, metadata_match: dict[str, Any] | None = None) -> int:
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(MAX(version),0) FROM assets WHERE project_id=? AND stage_id=? AND asset_type=?",
        (project_id, stage_id, asset_type),
    ).fetchone()
    conn.close()
    return row[0]


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

def create_feedback(asset_id: str, action: str, comment: str | None = None) -> FeedbackDict:
    conn = get_db()
    fb_id = _uuid()
    conn.execute(
        "INSERT INTO feedback (id, asset_id, action, comment, created_at) VALUES (?,?,?,?,?)",
        (fb_id, asset_id, action, comment, _now()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM feedback WHERE id=?", (fb_id,)).fetchone()
    conn.close()
    return dict(row)


# ---------------------------------------------------------------------------
# Soundtrack Config
# ---------------------------------------------------------------------------

def set_soundtrack_config(project_id: str, mode: str, uploaded_path: str | None = None) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO soundtrack_config (project_id, mode, uploaded_path) VALUES (?,?,?)",
        (project_id, mode, uploaded_path),
    )
    conn.commit()
    conn.close()


def get_soundtrack_config(project_id: str) -> SoundtrackConfigDict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM soundtrack_config WHERE project_id=?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_stage_all_approved(project_id: str, stage_number: int) -> bool:
    conn = get_db()
    stage = conn.execute("SELECT id FROM stages WHERE project_id=? AND stage_number=?", (project_id, stage_number)).fetchone()
    if not stage:
        conn.close()
        return False
    total = conn.execute("SELECT COUNT(*) FROM assets WHERE stage_id=?", (stage["id"],)).fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM assets WHERE stage_id=? AND status='approved'", (stage["id"],)).fetchone()[0]
    conn.close()
    return total > 0 and total == approved
