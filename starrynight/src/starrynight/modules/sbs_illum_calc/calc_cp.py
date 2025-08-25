"""Calculate illumination correction calculate invoke cellprofiler module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_illum_calc.constants import (
    SBS_ILLUM_CALC_CP_CPPIPE_OUT_NAME,
    SBS_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX,
    SBS_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX,
    SBS_ILLUM_CALC_OUT_PATH_SUFFIX,
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


class SBSCalcIllumInvokeCPModule(StarrynightModule):
    """SBSCalculate illumination invoke cellprofiler module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "sbs_calc_illum_invoke_cp"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "sbs_calc_illum_invoke_cp"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "cppipe_path": TypeInput(
                    name="Cellprofiler cppipe path",
                    type=TypeEnum.file,
                    description="Path to the cppipe file.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX,
                        SBS_ILLUM_CALC_CP_CPPIPE_OUT_NAME,
                    )
                    .resolve()
                    .__str__(),
                ),
                "loaddata_path": TypeInput(
                    name="loaddata_path",
                    type=TypeEnum.dir,
                    description="Path to the LoadData csv.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
            },
            outputs={
                "illum_path": TypeOutput(
                    name="Path to illum dir",
                    type=TypeEnum.dir,
                    description="Generated Illum correction files for the plate",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_ILLUM_CALC_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook path",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting generated illum corrections",
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
                        name="Starrynight SBS illum calculation invoke cellprofiler module",
                        description="This module invoke cellprofiler for generating sbs illumination corrections.",
                    )
                ]
            ),
        )

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
            spec.outputs["illum_path"].value,
            "--sbs",
        ]

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
                    },
                    output_paths={
                        "illum_path": [
                            spec.outputs["illum_path"].value.__str__()
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

    def _create_uow(self) -> list[UnitOfWork]:
        """Create units of work for Generate Index step.

        Returns
        -------
        list[UnitOfWork]
            List of unit of work.

        """
        return []
