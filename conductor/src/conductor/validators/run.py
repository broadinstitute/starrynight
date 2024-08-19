"""Run domain related validators."""

from pydantic import BaseModel

from conductor.constants import RunStatus


class Run(BaseModel):
    """Run create schema."""

    id: int | None = None
    job_id: int
    name: str
    run_status: RunStatus | None = None

    model_config: dict = {"from_attributes": True}
