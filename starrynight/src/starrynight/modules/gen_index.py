"""Generate index module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.schema import Container as SpecContainer
from starrynight.modules.schema import ExecFunction, TypeCitations
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


def create_pipe_gen_index(
    inventory_path: Path | CloudPath, out_dir: Path | CloudPath
) -> Pipeline:
    """Create pipeline for gen index.

    Parameters
    ----------
    inventory_path : Path | CloudPath
        Inventory path. Can be local or cloud.
    out_dir : Path | CloudPath
        Path to save outputs. Can be local or cloud.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    gen_index_pipe = Seq(
        [
            Container(
                "GenerateIndex",
                input_paths={"inventory": [inventory_path.resolve().__str__()]},
                output_paths={
                    "index": [out_dir.joinpath("index.parquet").resolve().__str__()]
                },
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=[
                        "starrynight",
                        "index",
                        "gen",
                        "-i",
                        inventory_path.resolve().__str__(),
                        "-o",
                        out_dir.resolve().__str__(),
                    ],
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
    def from_config(
        experiment: Experiment, data: DataConfig, spec: SpecContainer | None
    ) -> Self:
        """Create module from experiment and data config."""
        if spec is None:
            spec = SpecContainer(
                inputs=[],
                outputs=[],
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
                citations=TypeCitations(algorithm=[]),
            )
        pipe = create_pipe_gen_index(
            inventory_path=data.dataset_path,
            out_dir=data.storage_path.joinpath("inventory"),
        )
        uow = create_work_unit_gen_index(
            out_dir=data.storage_path.joinpath("inventory")
        )

        return GenIndexModule(spec=spec, pipe=pipe, uow=uow)
