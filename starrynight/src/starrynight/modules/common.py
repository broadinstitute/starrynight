"""Common tools for creating modules."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self, Unpack

import requests
from linkml.generators import PydanticGenerator
from pipecraft.node import UnitOfWork
from pipecraft.pipeline import Pipeline
from pydantic import BaseModel

from starrynight.experiments.common import Experiment
from starrynight.modules.schema import Container
from starrynight.schema import DataConfig


class StarrynightModule(BaseModel, ABC):
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

    @staticmethod
    @abstractmethod
    def from_config(
        experiment: Experiment,
        data: DataConfig,
        updated_spec_dict: dict[str, Container] = {},
        **kwargs: Unpack,
    ) -> Self:
        """Create module from experiment and data config."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def uid() -> str:
        """Return unique module id."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _spec() -> Container:
        """Return default spec of the module."""
        raise NotImplementedError


VALIDATE_SCHEMA_URL = "https://raw.githubusercontent.com/bilayer-containers/bilayers/master/tests/test_config/validate_schema.yaml"


def update_module_schema() -> None:
    """Download and update the module schema from bilayers."""
    schema_yaml = Path(__file__).parent.joinpath("validate_schema.yaml")
    schema_path = Path(__file__).parent.joinpath("schema.py")
    resp = requests.get(VALIDATE_SCHEMA_URL)
    if resp.status_code == 200:
        schema_yaml.open("wb").write(resp.content)
    else:
        raise Exception(
            "Unable to Download and update the module schema from bilayers."
        )

    # Write generated pydantic schema
    schema_path.open("w").write(PydanticGenerator(schema_yaml).serialize())


if __name__ == "__main__":
    update_module_schema()
