"""Run local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.run import create_run, fetch_all_runs
from conductor.validators.run import Run

run_router = APIRouter(prefix="/run", tags=["run"])


@run_router.post("/")
def post_run(request: Request, run: Run) -> Run:
    """Create run handler."""
    run.id = None
    return create_run(request.state.db_session, run)


@run_router.get("/")
def get_run(
    request: Request, job_id: int | None = None, limit: int = 20, offset: int = 0
) -> list[Run]:
    """Get run handler."""
    return fetch_all_runs(request.state.db_session, job_id, limit, offset)
