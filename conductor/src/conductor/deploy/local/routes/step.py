"""Step local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.step import (
    create_step,
    fetch_all_step_types,
    fetch_all_steps,
    fetch_step_count,
)
from conductor.validators.step import Step

step_router = APIRouter(prefix="/step", tags=["step"])


@step_router.post("/")
def post_step(request: Request, step: Step) -> Step:
    """Create step handler."""
    step.id = None
    return create_step(request.state.db_session, step)


@step_router.get("/")
def get_step(
    request: Request, project_id: int | None = None, limit: int = 20, offset: int = 0
) -> list[Step]:
    """Get step handler."""
    return fetch_all_steps(request.state.db_session, project_id, limit, offset)


@step_router.get("/type")
def get_step_type() -> list[str]:
    """Get step type handler."""
    return fetch_all_step_types()


@step_router.get("/count")
def get_step_count(request: Request, project_id: int | None = None) -> int:
    """Get step count handler."""
    return fetch_step_count(request.state.db_session, project_id)
