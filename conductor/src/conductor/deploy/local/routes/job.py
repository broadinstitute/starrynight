"""Job local route handlers."""

from fastapi import APIRouter, Request

from conductor.handlers.job import (
    create_job,
    execute_job,
    fetch_all_job_types,
    fetch_all_jobs,
    fetch_job_count,
    update_job,
)
from conductor.validators.job import Job
from conductor.validators.run import Run

job_router = APIRouter(prefix="/job", tags=["job"])


@job_router.post("/")
def post_job(request: Request, job: Job) -> Job:
    """Create job handler."""
    job.id = None
    return create_job(request.state.db_session, job)


@job_router.put("/")
def put_job(request: Request, job: Job) -> Job:
    """Update job handler."""
    return update_job(request.state.db_session, job)


@job_router.get("/")
def get_job(
    request: Request, project_id: int | None = None, limit: int = 40, offset: int = 0
) -> list[Job]:
    """Get job handler."""
    return fetch_all_jobs(request.state.db_session, project_id, limit, offset)


@job_router.get("/type")
def get_job_type() -> list[str]:
    """Get job type handler."""
    return fetch_all_job_types()


@job_router.get("/count")
def get_job_count(request: Request, project_id: int | None = None) -> int:
    """Get job count handler."""
    return fetch_job_count(request.state.db_session, project_id)


@job_router.post("/execute")
def job_execute(request: Request, job_id: int) -> Run:
    """Execute job."""
    return execute_job(request.state.db_session, job_id)
