"""Modules registry."""

from pipecraft.node import UnitOfWork
from pipecraft.pipeline import Pipeline
from pydantic import BaseModel

from starrynight.modules.schema import Container


class StarrynightModule(BaseModel):
    """Starrynight module interface.

    Attributes
    ----------
    spec : Module spec
    pipe : Module pipeline
    uow : Module unit of work

    """

    spec: Container
    pipe: Pipeline
    uow: list[UnitOfWork]

    class Config:
        """Model config."""

        arbitrary_types_allowed = True


MODULE_REGISTRY: dict[str, StarrynightModule] = {}
