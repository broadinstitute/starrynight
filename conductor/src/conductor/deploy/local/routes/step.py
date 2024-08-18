"""Step local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.step import create_step, fetch_all_steps
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
