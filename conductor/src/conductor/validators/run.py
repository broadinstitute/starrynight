"""Run domain related validators."""

from pipecraft.backend.base import BaseBackendRun
from pydantic import BaseModel
from starrynight.modules.schema import SpecContainer

from conductor.constants import ExecutorType, JobInputSchema, JobOutputSchema, RunStatus


class Run(BaseModel):
    """Run create schema."""

    id: int | None = None
    job_id: int
    name: str
    run_status: RunStatus | None = None
    executor_type: ExecutorType | None = None
    log_path: str | None = None
    spec: SpecContainer
    outputs: dict[str, JobOutputSchema]
    inputs: dict[str, JobInputSchema]
    backend_run: dict | None = None

    model_config: dict = {"from_attributes": True}
