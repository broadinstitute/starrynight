"""Project local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.project import (
    create_project,
    delete_project,
    fetch_all_parser_types,
    fetch_all_project_types,
    fetch_all_projects,
    fetch_project_by_id,
    fetch_project_count,
)
from conductor.validators.project import Project

project_router = APIRouter(prefix="/project", tags=["project"])


@project_router.post("/")
def post_project(request: Request, project: Project) -> Project:
    """Create project handler."""
    project.id = None
    return create_project(request.state.db_session, project)


@project_router.delete("/")
def remove_project(request: Request, project_id: int) -> Project:
    """Delete project handler."""
    return delete_project(request.state.db_session, project_id)


@project_router.get("/")
def get_project(request: Request, limit: int = 20, offset: int = 0) -> list[Project]:
    """Get project handler."""
    return fetch_all_projects(request.state.db_session, limit, offset)


@project_router.get("/id/{project_id}")
def get_project_by_id(request: Request, project_id: int) -> Project:
    """Get project by id handler."""
    return fetch_project_by_id(request.state.db_session, project_id)


@project_router.get("/type")
def get_project_type() -> list[str]:
    """Get project type handler."""
    return fetch_all_project_types()


@project_router.get("/parser-type")
def get_parser_type() -> list[str]:
    """Get parser type handler."""
    return fetch_all_parser_types()


@project_router.get("/count")
def get_project_count(request: Request) -> int:
    """Get project count handler."""
    return fetch_project_count(request.state.db_session)


@project_router.get("/execute")
def get_project_execute() -> str:
    """Get project execute handler."""
    return "test"
