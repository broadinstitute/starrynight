"""Run domain related validators."""

from pydantic import BaseModel


class Run(BaseModel):
    """Run create schema."""

    id: int | None = None
    job_id: int
    name: str

    model_config: dict = {"from_attributes": True}
