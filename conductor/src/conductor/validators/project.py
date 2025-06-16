"""Project domain related validators."""

from pydantic import BaseModel

from conductor.constants import ParserType


class Project(BaseModel):
    """Project create schema."""

    id: int | None = None
    name: str
    dataset_uri: str
    workspace_uri: str
    storage_uri: str
    init_config: dict = {}
    experiment: dict | None = {}
    img_uri: str | None = None
    description: str
    type: str
    parser_type: ParserType
    is_configured: bool

    model_config: dict = {"from_attributes": True}
