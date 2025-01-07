"""Job domain related validators."""

from pydantic import BaseModel
from starrynight.modules.schema import Container


class Job(BaseModel):
    """Job create schema."""

    id: int | None = None
    module_id: str
    step_id: int
    name: str
    description: str
    spec: Container

    model_config: dict = {"from_attributes": True}
