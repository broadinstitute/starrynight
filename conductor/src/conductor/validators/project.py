"""Project domain related validators."""

from pydantic import BaseModel

from conductor.constants import ParserType, ProjectType


class Project(BaseModel):
    """Project create schema."""

    id: int | None = None
    name: str
    dataset_uri: str
    img_uri: str | None = None
    description: str
    type: ProjectType
    parser_type: ParserType

    model_config: dict = {"from_attributes": True}
