"""Job domain related validators."""

from pydantic import BaseModel
from starrynight.modules.schema import SpecContainer


class Job(BaseModel):
    """Job create schema."""

    id: int | None = None
    uid: str
    name: str
    description: str
    spec: SpecContainer
    inputs: dict
    outputs: dict
    project_id: int

    model_config: dict = {"from_attributes": True}
