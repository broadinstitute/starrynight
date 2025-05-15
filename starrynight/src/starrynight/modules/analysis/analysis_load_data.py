"""Analysis gen loaddata module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.analysis.constants import (
    ANALYSIS_CP_LOADDATA_OUT_PATH_SUFFIX,
)
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_apply.constants import (
    CP_ILLUM_APPLY_OUT_PATH_SUFFIX,
)
from starrynight.modules.sbs_preprocess.constants import (
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


class AnalysisGenLoadDataModule(StarrynightModule):
    """Analysis generate loaddata module."""

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "analysis_gen_loaddata"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "index_path": TypeInput(
                    name="Project Index",
                    type=TypeEnum.file,
                    description="Path to the index.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        "index/index.parquet"
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
                "corrected_images_path": TypeInput(
                    name="Corrected images",
                    type=TypeEnum.dir,
                    description="Path to corrected images.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_ILLUM_APPLY_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "compensated_images_path": TypeInput(
                    name="Aligned and compensated images",
                    type=TypeEnum.dir,
                    description="Path to aligned and compensated images.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        SBS_PREPROCESS_OUT_PATH_SUFFIX
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
            },
            outputs={
                "loaddata_path": TypeOutput(
                    name="Cellprofiler LoadData csvs",
                    type=TypeEnum.dir,
                    description="Generated analysis loaddata files",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        ANALYSIS_CP_LOADDATA_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting load data files",
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
                        name="Starrynight Analysis generate loaddata module",
                        description="This module generates load data files for analysis module.",
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
            "analysis",
            "loaddata",
            "-i",
            spec.inputs["index_path"].value,
            "-o",
            spec.outputs["loaddata_path"].value,
            "--corr_images",
            spec.inputs["corrected_images_path"].value,
            "--comp_images",
            spec.inputs["compensated_images_path"].value,
        ]
        # Use user provided parser if available
        if spec.inputs["path_mask"].value is not None:
            cmd += ["--path_mask", spec.inputs["path_mask"].value]
        if spec.inputs["use_legacy"].value is True:
            assert spec.inputs["exp_config_path"].value is not None
            cmd += [
                "--use_legacy",
                "--exp_config",
                spec.inputs["exp_config_path"].value,
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
                        "loaddata_path": [
                            spec.outputs["loaddata_path"].value.__str__()
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
