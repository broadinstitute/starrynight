"""CPApplyulate illumination correction calculate gen cpipe module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_apply.constants import (
    CP_ILLUM_APPLY_CP_CPPIPE_OUT_PATH_SUFFIX,
    CP_ILLUM_APPLY_CP_LOADDATA_OUT_PATH_SUFFIX,
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
from starrynight.schema import DataConfig


class CPApplyIllumGenCPPipeModule(StarrynightModule):
    """CP Apply illumination generate cppipe module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "cp_apply_illum_gen_cppipe"

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "cp_apply_illum_gen_cppipe"

    def _spec(self) -> str:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "loaddata_path": TypeInput(
                    name="Cellprofiler LoadData csvs",
                    type=TypeEnum.dir,
                    description="Path to the LoadData csv.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_APPLY_CP_LOADDATA_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "workspace_path": TypeInput(
                    name="Workspace",
                    type=TypeEnum.dir,
                    description="Workspace path.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_APPLY_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "nuclei_channel": TypeInput(
                    name="Nuclei channel",
                    type=TypeEnum.textbox,
                    description="Which channel to use for nuclei segmentation.",
                    optional=False,
                    value=self.experiment.cp_config.nuclei_channel,
                ),
                "cell_channel": TypeInput(
                    name="Cell channel",
                    type=TypeEnum.textbox,
                    description="Which channel to use for cell segmentation.",
                    optional=False,
                    value=self.experiment.cp_config.cell_channel,
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
                    name="Cellprofiler pipeline",
                    type=TypeEnum.file,
                    description="Generated Illum calc cppipe files",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_APPLY_CP_CPPIPE_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook",
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
                        name="Starrynight CP illum apply generate cppipe module",
                        description="This module generates cppipe files for cp illumination correction apply module.",
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
            "apply",
            "cppipe",
            "-l",
            spec.inputs["loaddata_path"].value,
            "-o",
            spec.outputs["cppipe_path"].value,
            "-w",
            spec.inputs["workspace_path"].value,
            "--nuclei",
            spec.inputs["nuclei_channel"].value,
            "--cell",
            spec.inputs["cell_channel"].value,
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
