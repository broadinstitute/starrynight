"""Project domain related validators."""

from pydantic import BaseModel


class Project(BaseModel):
    """Project create schema."""

    id: int | None = None
    name: str

    model_config: dict = {"from_attributes": True}
