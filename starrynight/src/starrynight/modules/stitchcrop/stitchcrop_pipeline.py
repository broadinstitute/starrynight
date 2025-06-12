"""Stitchcrop gen pipeline module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.experiments.pcp_generic import PCPGeneric
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_apply.constants import (
    CP_ILLUM_APPLY_OUT_PATH_SUFFIX,
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
from starrynight.modules.stitchcrop.constants import (
    STITCHCROP_OUT_PATH_SUFFIX,
    STITCHCROP_PIPELINE_OUT_PATH_SUFFIX,
)
from starrynight.schema import DataConfig


class StitchcropGenPipelineModule(StarrynightModule):
    """Stitchcrop generate pipeline module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "stitchcrop_gen_pipeline"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "stitchcrop_gen_pipeline"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "index_path": TypeInput(
                    name="Project index",
                    type=TypeEnum.file,
                    description="Path to the index.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        "index/index.parquet"
                    )
                    .resolve()
                    .__str__(),
                ),
                "workspace_path": TypeInput(
                    name="Workspace",
                    type=TypeEnum.dir,
                    description="Workspace path.",
                    optional=True,
                    value=self.data_config.workspace_path.joinpath(
                        STITCHCROP_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "path_mask": TypeInput(
                    name="Path mask",
                    type=TypeEnum.textbox,
                    description="Path prefix mask to use.",
                    optional=True,
                ),
                "images_path": TypeInput(
                    name="Images to stitch",
                    type=TypeEnum.dir,
                    description="Path to images for stitching.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_APPLY_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "use_legacy": TypeInput(
                    name="Use legacy pipeline",
                    type=TypeEnum.boolean,
                    description="Flag for using legacy pipeline.",
                    optional=True,
                    value=False,
                ),
                "exp_config_path": TypeInput(
                    name="Experiment configuration json path",
                    type=TypeEnum.file,
                    description="Path to the generated experiment json file.",
                    optional=True,
                    value=self.data_config.workspace_path.joinpath(
                        "experiment/experiment.json"
                    )
                    .resolve()
                    .__str__(),
                ),
                "uow_list": TypeInput(
                    name="Unit of work list",
                    type=TypeEnum.file,
                    description="List of index columns to use for grouping runs.",
                    optional=True,
                ),
            },
            outputs={
                "pipeline_path": TypeOutput(
                    name="Fiji python pipeline",
                    type=TypeEnum.dir,
                    description="Generated python pipeline files",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        STITCHCROP_PIPELINE_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting pipeline files",
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
                        name="Starrynight Stithcrop generate pipeline module",
                        description="This module generates pipeline files for stitchcrop module.",
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
        """Create pipeline for generating load data.

        Returns
        -------
        Pipeline
            Pipeline instance.

        """
        spec = self.spec
        cmd = [
            "starrynight",
            "stitchcrop",
            "pipeline",
            "-i",
            spec.inputs["index_path"].value,
            "-o",
            spec.outputs["pipeline_path"].value,
            "-w",
            spec.inputs["workspace_path"].value,
            "--images",
            spec.inputs["images_path"].value,
            "--exp_config",
            spec.inputs["exp_config_path"].value,
        ]
        if spec.inputs["path_mask"].value is not None:
            cmd += ["--path_mask", spec.inputs["path_mask"].value]

        if spec.inputs["uow_list"].value is not None:
            cmd += ["--uow", spec.inputs["uow_list"].value]

        if spec.inputs["use_legacy"].value is True:
            cmd += [
                "--use_legacy",
            ]
        gen_load_data_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={
                        "index_path": [
                            spec.inputs["index_path"].value.__str__()
                        ]
                    },
                    output_paths={
                        "pipeline_path": [
                            spec.outputs["pipeline_path"].value.__str__()
                        ]
                    },
                    config=ContainerConfig(
                        image="ghrc.io/leoank/starrynight:dev",
                        cmd=cmd,
                        env={},
                    ),
                ),
            ]
        )
        return gen_load_data_pipe
