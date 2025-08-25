"""Stitchcrop invoke fiji module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_stitchcrop.constants import (
    SBS_STITCHCROP_OUT_PATH_SUFFIX,
    SBS_STITCHCROP_PIPELINE_OUT_PATH_SUFFIX,
)
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


class SBSStitchcropInvokeFijiModule(StarrynightModule):
    """SBS Stitchcrop invoke fiji module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "sbs_stitchcrop_invoke_fiji"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "sbs_stitchcrop_invoke_fiji"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "pipeline_path": TypeInput(
                    name="Fiji pipeline",
                    type=TypeEnum.dir,
                    description="Path to the python pipelines directory.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_STITCHCROP_PIPELINE_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "fiji_path": TypeInput(
                    name="Fiji executable",
                    type=TypeEnum.dir,
                    description="Path to the fiji executable.",
                    optional=True,
                ),
            },
            outputs={
                "stitched_images_path": TypeOutput(
                    name="Stitched images",
                    type=TypeEnum.dir,
                    description="Stitched images after preprocessing",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_STITCHCROP_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting stitched images",
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
                        name="Starrynight SBS Stitchcrop invoke fiji module",
                        description="This module invoke fiji for stitching images.",
                    )
                ]
            ),
        )

    def _create_uow(self) -> list[UnitOfWork]:
        """Create units of work for Generate Index step.

        Returns
        -------
        list[UnitOfWork]
            List of unit of work.

        """
        return []

    def _create_pipe(self) -> Pipeline:
        """Create pipeline for invoking cellprofiler.

        Returns
        -------
        Pipeline
            Pipeline instance.

        """
        spec = self.spec
        cmd = [
            "starrynight",
            "stitchcrop",
            "fiji",
            "-p",
            spec.inputs["pipeline_path"].value,
        ]

        if spec.inputs["fiji_path"].value:
            cmd += ["-f", spec.inputs["fiji_path"].value]

        gen_load_data_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={
                        "pipeline_path": [
                            AnyPath(
                                spec.inputs["pipeline_path"].value
                            ).parent.__str__()
                        ],
                    },
                    output_paths={
                        "stitched_images_path": [
                            spec.outputs["stitched_images_path"].value.__str__()
                        ]
                    },
                    config=ContainerConfig(
                        image="ghcr.io/leoank/starrynight:dev",
                        cmd=cmd,
                        env={},
                    ),
                ),
            ]
        )
        return gen_load_data_pipe
