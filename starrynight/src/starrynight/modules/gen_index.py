"""Generate index module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.schema import (
    Container as SpecContainer,
)
from starrynight.modules.schema import (
    ExecFunction,
    TypeAlgorithmFromCitation,
    TypeCitations,
    TypeEnum,
    TypeInput,
    TypeOutput,
)
from starrynight.schema import DataConfig


def create_work_unit_gen_index(out_dir: Path | CloudPath) -> list[UnitOfWork]:
    """Create units of work for Generate Index step.

    Parameters
    ----------
    out_dir : Path | CloudPath
        Path to load data csv. Can be local or cloud.

    Returns
    -------
    list[UnitOfWork]
        List of unit of work.

    """
    uow_list = [
        UnitOfWork(
            inputs={
                "inventory": [out_dir.joinpath("inventory.parquet").resolve().__str__()]
            },
            outputs={"index": [out_dir.joinpath("index.parquet").resolve().__str__()]},
        )
    ]

    return uow_list


def create_pipe_gen_index(uid: str, spec: SpecContainer) -> Pipeline:
    """Create pipeline for gen index.

    Parameters
    ----------
    uid: str
        Module unique id.
    spec: SpecContainer
        GenIndexModule specification.
    inventory_path : Path | CloudPath
        Inventory path. Can be local or cloud.
    out_dir : Path | CloudPath
        Path to save outputs. Can be local or cloud.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "index",
        "gen",
        "-i",
        spec.inputs[0].path,
        "-o",
        Path(spec.outputs[0].path).parent.resolve().__str__(),
    ]
    # Use user provided parser if available
    if spec.inputs[1].path is not None:
        cmd += ["--parser", spec.inputs[1].path]
    gen_index_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={"inventory": [spec.inputs[0].path]},
                output_paths={"index": [spec.outputs[0].path]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=cmd,
                    env={},
                ),
            ),
        ]
    )
    return gen_index_pipe


class GenIndexModule(StarrynightModule):
    """Generate Index module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "generate_index"

    @staticmethod
    def _spec() -> str:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="inventory_path",
                    type=TypeEnum.files,
                    description="Path to the inventory.",
                    optional=False,
                    path="path/to/the/inventory",
                ),
                TypeInput(
                    name="parser_path",
                    type=TypeEnum.file,
                    description="Path to a custom parser grammar file.",
                    optional=True,
                    path=None,
                ),
            ],
            outputs=[
                TypeOutput(
                    name="project_index",
                    type=TypeEnum.file,
                    description="Generated Index",
                    optional=False,
                    path="random/path/to/index.parquet",
                ),
                TypeOutput(
                    name="index_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting index",
                    optional=False,
                    path="http://karkinos:2720/?file=.%2FindexOutput.py",
                ),
            ],
            parameters=[],
            display_only=[],
            results=[],
            exec_function=ExecFunction(
                name="",
                script="",
                module="",
                cli_command="",
            ),
            docker_image=None,
            algorithm_folder_name=None,
            citations=TypeCitations(
                algorithm=[
                    TypeAlgorithmFromCitation(
                        name="Starrynight indexing module",
                        description="This module generates an index for the dataset.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> Self:
        """Create module from experiment and data config."""
        if spec is None:
            spec = GenIndexModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath("inventory/inventory.parquet")
                .resolve()
                .__str__()
            )
            spec.outputs[0].path = (
                data.workspace_path.joinpath("index/index.parquet").resolve().__str__()
            )
        pipe = create_pipe_gen_index(
            uid=GenIndexModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return GenIndexModule(spec=spec, pipe=pipe, uow=uow)
