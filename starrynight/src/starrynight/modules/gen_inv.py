"""Generate Inventory module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
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


class GenInvModule(StarrynightModule):
    """Generate Inventory module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "generate_inventory"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "generate_inventory"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "dataset_path": TypeInput(
                    name="Dataset path",
                    type=TypeEnum.dir,
                    description="Path to the dataset.",
                    optional=False,
                    value=self.data_config.dataset_path.resolve().__str__(),
                ),
            },
            outputs={
                "project_inventory": TypeOutput(
                    name="Inventory path",
                    type=TypeEnum.file,
                    description="Generated Inventory",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        "inventory/inventory.parquet"
                    )
                    .resolve()
                    .__str__(),
                )
            },
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

    def _create_pipe(self) -> Pipeline:
        """Create pipeline for gen inv.

        Returns
        -------
        Pipeline
            Pipeline instance.

        """
        spec = self.spec
        cmd = [
            "starrynight",
            "inventory",
            "gen",
            "-d",
            spec.inputs["dataset_path"].value,
            "-o",
            Path(spec.outputs["project_inventory"].value).parent.__str__(),
        ]

        gen_inv_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={},
                    output_paths={
                        "inventory": [spec.outputs["project_inventory"].value]
                    },
                    config=ContainerConfig(
                        image="ghrc.io/leoank/starrynight:dev",
                        cmd=cmd,
                        env={},
                    ),
                ),
            ]
        )
        return gen_inv_pipe

    def _create_uow(self) -> list[UnitOfWork]:
        """Create units of work for Generate Inv step.

        Returns
        -------
        list[UnitOfWork]
            List of unit of work.

        """
        return []
