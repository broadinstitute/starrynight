"""Common tools for creating modules."""

from abc import ABC, abstractmethod, abstractproperty
from inspect import getdoc, signature
from pathlib import Path
from typing import Callable, Generic, Self, TypeVar, Unpack

import requests
from linkml.generators import PydanticGenerator
from numpydoc.docscrape import NumpyDocString
from pipecraft.node import Container as PipeContainer
from pipecraft.node import ContainerConfig as PipeContainerConfig
from pipecraft.node import UnitOfWork
from pipecraft.pipeline import Pipeline, Seq
from pydantic import BaseModel

from starrynight.experiments.common import Experiment
from starrynight.modules.schema import (
    ExecFunction,
    SpecContainer,
    TypeAlgorithmFromCitation,
    TypeCitations,
    TypeEnum,
    TypeInput,
    TypeOutput,
)
from starrynight.schema import DataConfig


class StarrynightModule(BaseModel, ABC):
    """Starrynight module interface.

    Attributes
    ----------
    data_config: Module data configuration
    spec : Module spec
    pipe : Module pipeline
    uow : Module unit of work

    """

    data_config: DataConfig
    experiment: Experiment | None
    spec: SpecContainer | None

    @property
    @abstractmethod
    def uid() -> str:
        """Return unique module id."""
        raise NotImplementedError

    @abstractmethod
    def _spec(self: Self) -> SpecContainer:
        """Return default spec of the module."""
        raise NotImplementedError

    @abstractmethod
    def _create_pipe(self: Self) -> Pipeline:
        """Create pipeline."""
        raise NotImplementedError

    @abstractmethod
    def _create_uow(self: Self) -> list[UnitOfWork]:
        """Create units of work."""
        raise NotImplementedError

    @property
    def pipe(self: Self) -> Pipeline:
        """Module pipeline property."""
        return self._create_pipe()

    @property
    def uow(self: Self) -> Pipeline:
        """Module unit of work property."""
        return self._create_uow()

    class Config:
        """Model config."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        data_config: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
        /,
        **data: Unpack,
    ) -> None:
        """Init Starrynight module."""
        # First init pydantic model with an empty spec
        super().__init__(
            data_config=data_config, experiment=experiment, spec=None, **data
        )
        # If no spec provided by the user then generate default spec
        if spec is None:
            spec = self._spec()

        # Init again with spec ( We validate the spec here)
        super().__init__(
            data_config=data_config, experiment=experiment, spec=spec, **data
        )


_P = TypeVar("_P")
_R = TypeVar("_R")

TYPE_MAP = {
    "Path | CloudPath": TypeEnum.dir,
    "str": TypeEnum.textbox,
    "bool": TypeEnum.boolean,
}


class StarrynightDecoratedFunction(Generic[_P, _R]):
    """Wrapper for converting a function to a Starrynight modules.

    Parameters
    ----------
    func: Callable

    """

    def __init__(
        self,
        func: Callable[_P, _R],
        module_uid: str,
        cli_suffix: list[str],
        container_img: str,
    ) -> None:
        """Init module."""
        self._func = func
        self._module_uid = module_uid
        self._sig = signature(self._func)
        self._params = self._sig.parameters
        self._return_ano = self._sig.return_annotation
        self._cli_suffix = cli_suffix
        self._container_img = container_img
        self.cli = self._gen_cli()
        self.module = self._gen_module()

    def __call__(self, *args, **kwargs) -> _R:
        pass

    def _gen_cli(self) -> Callable:
        pass

    def _gen_pipe_from_anno(self, spec: SpecContainer) -> Pipeline:
        parsed_doc = NumpyDocString(getdoc(self._func))
        cmd = []
        return Seq(
            [
                PipeContainer(
                    name="",
                    input_paths={
                        input.name: [Path(input.path).parent.__str__()]
                        for input in spec.inputs
                    },
                    output_paths={
                        output.name: [Path(output.path).parent.__str__()]
                        for output in spec.outputs
                    },
                    config=PipeContainerConfig(
                        image=self._container_img,
                        cmd=cmd,
                        env={},
                    ),
                ),
            ]
        )

    def _gen_spec_from_anno(self) -> SpecContainer:
        parsed_doc = NumpyDocString(getdoc(self._func))
        return SpecContainer(
            inputs=[
                TypeInput(
                    name=param.name,
                    type=TYPE_MAP[param.type],
                    description=param.desc,
                    optional=False,
                    path="path/to/the/somewhere",
                )
                for param in parsed_doc["Parameters"]
            ],
            outputs=[
                TypeOutput(
                    name="out",
                    type=TYPE_MAP[param.type],
                    description=param.desc,
                    optional=False,
                    path="path/to/the/somewhere",
                )
                for param in parsed_doc["Returns"]
            ],
            citations=TypeCitations(
                algorithm=[
                    TypeAlgorithmFromCitation(
                        name=parsed_doc["References"][0],
                        description=parsed_doc["References"][2],
                    )
                ]
            ),
        )

    def _gen_module(self) -> StarrynightModule:
        def uid() -> str:
            return self._module_uid

        spec = self._gen_spec_from_anno()
        pipe = self._gen_pipe_from_anno(spec)
        uow = []
        mod = StarrynightModule(spec, pipe, uow)
        mod.uid = uid
        return mod

    def show(self) -> None:
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
