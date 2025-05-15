"""SBS Preprocess gen cpipe module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.experiments.pcp_generic import PCPGeneric
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_preprocess.constants import (
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


class SBSPreprocessGenCPPipeModule(StarrynightModule):
    """SBS preprocess cppipe module."""

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "sbs_preprocess_gen_cppipe"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
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
                "workspace_path": TypeInput(
                    name="Workspace",
                    type=TypeEnum.dir,
                    description="Workspace path.",
                    optional=True,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_PREPROCESS_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "barcode_csv_path": TypeInput(
                    name="Barcode csv",
                    type=TypeEnum.file,
                    description="Path to barcode csv.",
                    optional=False,
                    value=self.experiment.sbs_config.barcode_csv_path.resolve().__str__(),
                ),
                "nuclei_channel": TypeInput(
                    name="Nuclei channel",
                    type=TypeEnum.textbox,
                    description="Name of the nuclei channel.",
                    optional=False,
                    value=self.experiment.sbs_config.nuclei_channel,
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
                    description="Generated sbs preprocess cppipe files",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_PREPROCESS_CP_CPPIPE_OUT_PATH_SUFFIX
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
                        name="Starrynight SBS preprocess generate cppipe module",
                        description="This module generates cppipe files for sbs preprocess module.",
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
            "preprocess",
            "cppipe",
            "-l",
            spec.inputs["loaddata_path"].value,
            "-o",
            spec.outputs["cppipe_path"].value,
            "-w",
            spec.inputs["workspace_path"].value,
            "-b",
            spec.inputs["barcode_csv_path"].value,
            "-n",
            spec.inputs["nuclei_channel"].value,
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
                        "loaddata_path": [
                            spec.inputs["loaddata_path"].value.__str__()
                        ]
                    },
                    output_paths={
                        "cppipe_path": [
                            spec.outputs["cppipe_path"].value.__str__()
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
