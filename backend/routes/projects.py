"""Friday Studio — Project CRUD routes."""

from fastapi import APIRouter, HTTPException

from backend.database import create_project, list_projects, get_project
from backend.models import ProjectCreate

router = APIRouter(tags=["projects"])


@router.post("/projects")
def api_create_project(body: ProjectCreate):
    project = create_project(body.title, body.brief)
    return project


@router.get("/projects")
def api_list_projects():
    return list_projects()


@router.get("/projects/{project_id}")
def api_get_project(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project
