"""SBS preprocess invoke cellprofiler module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_illum_apply.constants import (
    SBS_ILLUM_APPLY_OUT_PATH_SUFFIX,
)
from starrynight.modules.sbs_preprocess.constants import (
    SBS_PREPROCESS_CP_CPPIPE_OUT_NAME,
    SBS_PREPROCESS_CP_CPPIPE_OUT_PATH_SUFFIX,
    SBS_PREPROCESS_CP_LOADDATA_OUT_PATH_SUFFIX,
    SBS_PREPROCESS_OUT_PATH_SUFFIX,
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


class SBSPreprocessInvokeCPModule(StarrynightModule):
    """SBS Preprocess invoke cellprofiler module."""

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "sbs_preprocess_invoke_cp"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "cppipe_path": TypeInput(
                    name="Cellprofiler pipeline",
                    type=TypeEnum.file,
                    description="Path to the cppipe file.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_PREPROCESS_CP_CPPIPE_OUT_PATH_SUFFIX,
                        SBS_PREPROCESS_CP_CPPIPE_OUT_NAME,
                    )
                    .resolve()
                    .__str__(),
                ),
                "loaddata_path": TypeInput(
                    name="Cellprofiler LoadData csvs",
                    type=TypeEnum.dir,
                    description="Path to the LoadData csv.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_PREPROCESS_CP_LOADDATA_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "plugin_path": TypeInput(
                    name="Cellprofiler plugin directory",
                    type=TypeEnum.dir,
                    description="Path to the cellprofiler plugins.",
                    optional=False,
                ),
            },
            outputs={
                "compensated_images_path": TypeOutput(
                    name="Aligned and compensated images",
                    type=TypeEnum.dir,
                    description="Aligned and compensated images after preprocessing",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_PREPROCESS_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting illum corrections",
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
                        name="Starrynight SBS Preprocess invoke cellprofiler module",
                        description="This module invoke cellprofiler for sbs preprocess.",
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
            "cp",
            "-p",
            spec.inputs["cppipe_path"].value,
            "-l",
            spec.inputs["loaddata_path"].value,
            "-o",
            spec.outputs["compensated_images_path"].value,
            "--sbs",
        ]

        if spec.inputs["plugin_path"]:
            cmd += ["--plugin_dir", spec.inputs["plugin_path"]]

        gen_load_data_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={
                        "cppipe_path": [
                            AnyPath(
                                spec.inputs["cppipe_path"].value
                            ).parent.__str__()
                        ],
                        "loaddata_path": [
                            spec.inputs["loaddata_path"].value.__str__()
                        ],
                        "sbs_illum_apply_path": [
                            self.data_config.workspace_path.joinpath(
                                SBS_ILLUM_APPLY_OUT_PATH_SUFFIX
                            )
                            .resolve()
                            .__str__()
                        ],
                    },
                    output_paths={
                        "compensated_images_path": [
                            spec.outputs[
                                "compensated_images_path"
                            ].value.__str__()
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
