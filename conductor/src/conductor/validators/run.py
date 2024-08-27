"""Run domain related validators."""

from pydantic import BaseModel

from conductor.constants import ExecutorType, JobInputSchema, JobOutputSchema, RunStatus


class Run(BaseModel):
    """Run create schema."""

    id: int | None = None
    job_id: int
    name: str
    run_status: RunStatus | None = None
    executor_type: ExecutorType | None = None
    log_path: str | None = None
    outputs: dict[str, JobOutputSchema]
    inputs: dict[str, JobInputSchema]

    model_config: dict = {"from_attributes": True}
