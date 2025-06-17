"""Project local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.project import (
    configure_project,
    create_project,
    delete_project,
    execute_project,
    fetch_all_parser_types,
    fetch_all_project_types,
    fetch_all_projects,
    fetch_project_by_id,
    fetch_project_count,
    fetch_project_details_by_type,
    update_project,
)
from conductor.validators.project import Project
from conductor.validators.run import Run

project_router = APIRouter(prefix="/project", tags=["project"])


@project_router.post("/")
def post_project(request: Request, project: Project) -> Project:
    """Create project handler."""
    project.id = None
    project.is_configured = False
    return create_project(request.state.db_session, project)


@project_router.put("/")
def put_project(request: Request, project: Project) -> Project:
    """Update project handler."""
    return update_project(request.state.db_session, project)


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


@project_router.get("/type/all")
def get_project_type() -> list[str]:
    """Get all project type handler."""
    return fetch_all_project_types()


@project_router.get("/type/{project_type}")
def get_project_type_details(project_type: str) -> dict | None:
    """Get project init details handler."""
    return fetch_project_details_by_type(project_type)


@project_router.get("/parser-type")
def get_parser_type() -> list[str]:
    """Get parser type handler."""
    return fetch_all_parser_types()


@project_router.get("/count")
def get_project_count(request: Request) -> int:
    """Get project count handler."""
    return fetch_project_count(request.state.db_session)


@project_router.post("/execute")
def post_project_execute(request: Request, project_id: int) -> Run:
    """Get project execute handler."""
    return "test"


@project_router.post("/configure")
def post_configure_project(request: Request, project_id: int) -> Project:
    """Configure project by id handler."""
    return configure_project(request.state.db_session, project_id)


@project_router.post("/execute")
def project_execute(request: Request, project_id: int) -> Run:
    """Execute project."""
    return execute_project(request.state.db_session, project_id)
