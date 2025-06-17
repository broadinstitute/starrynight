"""CPCalculate illumination correction calculate gen cpipe module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_calc.constants import (
    CP_ILLUM_CALC_CP_CPPIPE_OUT_NAME,
    CP_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX,
    CP_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX,
    CP_ILLUM_CALC_OUT_PATH_SUFFIX,
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


class CPCalcIllumGenCPPipeModule(StarrynightModule):
    """CPCalculate illumination generate cppipe module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "calc_illum_gen_cppipe"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "calc_illum_gen_cppipe"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "loaddata_path": TypeInput(
                    name="Cellprofiler LoadData path",
                    type=TypeEnum.dir,
                    description="Path to the LoadData csv.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "workspace_path": TypeInput(
                    name="Workspace path",
                    type=TypeEnum.file,
                    description="Workspace path.",
                    optional=True,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_CALC_OUT_PATH_SUFFIX
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
            },
            outputs={
                "cppipe_path": TypeOutput(
                    name="Cellprofiler pipeline path",
                    type=TypeEnum.dir,
                    description="Generated Illum calc cppipe files",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX,
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook path",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting cellprofiler pipeline files",
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
                        name="Starrynight CP illum calculation generate cppipe module",
                        description="This module generates cppipe files for illumination corrections module.",
                    )
                ]
            ),
        )

    def _create_pipe(self) -> Pipeline:
        """Create pipeline for generating cpipe.

        Returns
        -------
        Pipeline
            Pipeline instance.

        """
        spec = self.spec
        cmd = [
            "starrynight",
            "illum",
            "calc",
            "cppipe",
            "-l",
            spec.inputs["loaddata_path"].value,
            "-o",
            spec.outputs["cppipe_path"].value,
            "-w",
            spec.inputs["workspace_path"].value,
        ]
        if spec.inputs["use_legacy"].value is True:
            cmd += [
                "--use_legacy",
            ]

        gen_load_data_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={
                        "loaddata_path": [spec.inputs["loaddata_path"].value]
                    },
                    output_paths={
                        "cppipe_path": [spec.outputs["cppipe_path"].value]
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

    def _create_uow(self) -> list[UnitOfWork]:
        """Create units of work for Generate Index step.

        Returns
        -------
        list[UnitOfWork]
            List of unit of work.

        """
        return []
