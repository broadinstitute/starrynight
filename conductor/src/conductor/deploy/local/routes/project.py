"""Project local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.project import create_project, fetch_all_projects
from conductor.validators.project import Project

project_router = APIRouter(prefix="/project", tags=["project"])


@project_router.post("/")
def post_project(request: Request, project: Project) -> Project:
    """Create project handler."""
    project.id = None
    return create_project(request.state.db_session, project)


@project_router.get("/")
def get_project(request: Request, limit: int = 20, offset: int = 0) -> list[Project]:
    """Get project handler."""
    return fetch_all_projects(request.state.db_session, limit, offset)
