"""Generate Inventory module."""

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


def create_work_unit_gen_inv(out_dir: Path | CloudPath) -> list[UnitOfWork]:
    """Create units of work for Generate Inv step.

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
            inputs={},
            outputs={
                "inventory": [out_dir.joinpath("inventory.parquet").resolve().__str__()]
            },
        )
    ]

    return uow_list


def create_pipe_gen_inv(
    uid: str,
    spec: SpecContainer,
) -> Pipeline:
    """Create pipeline for gen inv.

    Parameters
    ----------
    uid: str
        Module unique id.
    spec: SpecContainer
        GenInvModule specification.
    dataset_path : Path | CloudPath
        Dataset path. Can be local or cloud.
    out_dir : Path | CloudPath
        Path to save outputs. Can be local or cloud.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "inventory",
        "gen",
        "-d",
        spec.inputs[0].path,
        "-o",
        Path(spec.outputs[0].path).parent.__str__(),
    ]

    # Use user provided parser if available
    if spec.inputs[1].path is not None:
        cmd += ["-p", spec.inputs[1].path]

    gen_inv_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={},
                output_paths={"inventory": [spec.outputs[0].path]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=cmd,
                    env={},
                ),
            ),
        ]
    )
    return gen_inv_pipe


class GenInvModule(StarrynightModule):
    """Generate Inventory module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "generate_inventory"

    @staticmethod
    def _spec() -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="dataset_path",
                    type=TypeEnum.files,
                    description="Path to the dataset.",
                    optional=False,
                    path="path/to/the/dataset",
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
                    name="project_inventory",
                    type=TypeEnum.file,
                    description="Generated Inventory",
                    optional=False,
                    path="random/path/to/inventory.parquet",
                )
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
                        name="Starrynight inventory module",
                        description="This module generates an inventory for the dataset.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        experiment: Experiment, data: DataConfig, spec: SpecContainer | None
    ) -> Self:
        """Create module from experiment and data config."""
        if spec is None:
            spec = GenInvModule._spec()
            spec.inputs[0].path = data.dataset_path.resolve().__str__()
            spec.outputs[0].path = (
                data.storage_path.joinpath("inventory/inventory.parquet")
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_inv(uid=GenInvModule.uid(), spec=spec)
        uow = create_work_unit_gen_inv(out_dir=data.storage_path.joinpath("inventory"))

        return GenInvModule(spec=spec, pipe=pipe, uow=uow)
