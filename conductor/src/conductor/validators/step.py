"""Project domain related validators."""

from pydantic import BaseModel

from conductor.constants import StepType


class Step(BaseModel):
    """Step create schema."""

    id: int | None = None
    project_id: int
    name: str
    description: str
    type: StepType

    model_config: dict = {"from_attributes": True}
