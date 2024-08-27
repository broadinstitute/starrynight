"""Job domain related validators."""

from pydantic import BaseModel

from conductor.constants import JobInputSchema, JobOutputSchema, JobType


class Job(BaseModel):
    """Job create schema."""

    id: int | None = None
    step_id: int
    name: str
    description: str
    type: JobType
    outputs: dict[str, JobOutputSchema]
    inputs: dict[str, JobInputSchema]

    model_config: dict = {"from_attributes": True}
