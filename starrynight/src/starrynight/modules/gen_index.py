"""Generate index module."""

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


class GenIndexModule(StarrynightModule):
    """Generate Index module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "generate_index"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "generate_index"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "inventory_path": TypeInput(
                    name="inventory_path",
                    type=TypeEnum.file,
                    description="Path to the inventory.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        "inventory/inventory.parquet"
                    )
                    .resolve()
                    .__str__(),
                ),
                "parser_path": TypeInput(
                    name="parser_path",
                    type=TypeEnum.file,
                    description="Path to a custom parser grammar file.",
                    optional=True,
                ),
            },
            outputs={
                "project_index_path": TypeOutput(
                    name="project_index",
                    type=TypeEnum.file,
                    description="Generated Index",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        "index/index.parquet"
                    )
                    .resolve()
                    .__str__(),
                ),
                "index_notebook_path": TypeOutput(
                    name="index_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting index",
                    optional=False,
                ),
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
                        name="Starrynight indexing module",
                        description="This module generates an index for the dataset.",
                    )
                ]
            ),
        )

    def _create_pipe(self) -> Pipeline:
        """Create pipeline for gen index.

        Returns
        -------
        Pipeline
            Pipeline instance.

        """
        spec = self.spec
        cmd = [
            "starrynight",
            "index",
            "gen",
            "-i",
            spec.inputs["inventory_path"].value,
            "-o",
            Path(spec.outputs["project_index_path"].value)
            .parent.resolve()
            .__str__(),
        ]
        # Use user provided parser if available
        if spec.inputs["parser_path"].value is not None:
            cmd += ["--parser", spec.inputs["parser_path"].value]
        gen_index_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={
                        "inventory": [spec.inputs["inventory_path"].value]
                    },
                    output_paths={
                        "index": [spec.outputs["project_index_path"].value]
                    },
                    config=ContainerConfig(
                        image="ghcr.io/leoank/starrynight:dev",
                        cmd=cmd,
                        env={},
                    ),
                ),
            ]
        )
        return gen_index_pipe

    def _create_uow(self) -> list[UnitOfWork]:
        """Create units of work for Generate Index step.

        Returns
        -------
        list[UnitOfWork]
            List of unit of work.

        """
        # TODO: Think and implement the uow interface
        return []
