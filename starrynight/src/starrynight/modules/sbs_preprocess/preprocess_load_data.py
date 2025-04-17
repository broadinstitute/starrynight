"""SBS preprocess gen loaddata module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.experiments.pcp_generic import PCPGeneric
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_align.constants import SBS_ALIGN_OUT_PATH_SUFFIX
from starrynight.modules.sbs_illum_apply.constants import (
    SBS_ILLUM_APPLY_OUT_PATH_SUFFIX,
)
from starrynight.modules.sbs_preprocess.constants import (
    SBS_PREPROCESS_CP_LOADDATA_OUT_PATH_SUFFIX,
)
from starrynight.modules.schema import (
    Container as SpecContainer,
)
from starrynight.modules.schema import (
    ExecFunction,
    TypeAlgorithmFromCitation,
    TypeCitations,
    TypeEnum,
    TypeInput,
    TypeOutput,
)
from starrynight.schema import DataConfig


def create_work_unit_gen_index(out_dir: Path | CloudPath) -> list[UnitOfWork]:
    """Create units of work for Generate Index step.

    Parameters
    ----------
    out_dir : Path | CloudPath
        Path to load data csv. Can be local or cloud.

    Returns
    -------
    list[UnitOfWork]
        List of unit of work.

    """
    uow_list = [
        UnitOfWork(
            inputs={
                "inventory": [
                    out_dir.joinpath("inventory.parquet").resolve().__str__()
                ]
            },
            outputs={
                "index": [out_dir.joinpath("index.parquet").resolve().__str__()]
            },
        )
    ]

    return uow_list


def create_pipe_gen_load_data(uid: str, spec: SpecContainer) -> Pipeline:
    """Create pipeline for generating load data.

    Parameters
    ----------
    uid: str
        Module unique id.
    spec: SpecContainer
        SBSPreprocessModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "preprocess",
        "loaddata",
        "-i",
        spec.inputs[0].path,
        "-o",
        spec.outputs[0].path,
        "-c",
        spec.inputs[2].path,
        "-a",
        spec.inputs[3].path,
        "-n",
        spec.inputs[4].path,
    ]
    # Use user provided parser if available
    if spec.inputs[1].path is not None:
        cmd += ["--path_mask", spec.inputs[1].path]
    gen_load_data_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={"index": [spec.inputs[0].path.__str__()]},
                output_paths={
                    "load_data_path": [spec.outputs[0].path.__str__()]
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


class SBSPreprocessGenLoadDataModule(StarrynightModule):
    """SBS Preprocess generate loaddata module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "sbs_preprocess_gen_loaddata"

    @staticmethod
    def _spec() -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="index_path",
                    type=TypeEnum.files,
                    description="Path to the index.",
                    optional=False,
                    path="path/to/the/index",
                ),
                TypeInput(
                    name="path_mask",
                    type=TypeEnum.file,
                    description="Path prefix mask to use.",
                    optional=True,
                    path=None,
                ),
                TypeInput(
                    name="corr_images_path",
                    type=TypeEnum.file,
                    description="Path to corrected images.",
                    optional=False,
                    path=None,
                ),
                TypeInput(
                    name="align_images_path",
                    type=TypeEnum.file,
                    description="Path to aligned images.",
                    optional=False,
                    path=None,
                ),
                TypeInput(
                    name="nuclei_channel",
                    type=TypeEnum.textbox,
                    description="Name of the nuclei channel.",
                    optional=False,
                    path=None,
                ),
            ],
            outputs=[
                TypeOutput(
                    name="sbs_preprocess_loaddata",
                    type=TypeEnum.files,
                    description="Generated Preprocess loaddata files",
                    optional=False,
                    path="random/path/to/loaddata_dir",
                ),
                TypeOutput(
                    name="loaddata_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting load data files",
                    optional=False,
                    path="http://karkinos:2720/?file=.%2FillumSBSApplyOutput.py",
                ),
            ],
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
                        name="Starrynight SBS Preprocess generate loaddata module",
                        description="This module generates load data files for sbs preprocess module.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> "SBSPreprocessGenLoadDataModule":
        """Create module from experiment and data config."""
        if spec is None:
            spec = SBSPreprocessGenLoadDataModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath("index/index.parquet")
                .resolve()
                .__str__()
            )
            spec.inputs[2].path = (
                data.workspace_path.joinpath(SBS_ILLUM_APPLY_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
            spec.inputs[3].path = (
                data.workspace_path.joinpath(SBS_ALIGN_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
            assert isinstance(experiment, PCPGeneric)
            spec.inputs[4].path = experiment.sbs_config.nuclei_channel
            spec.outputs[0].path = (
                data.workspace_path.joinpath(
                    SBS_PREPROCESS_CP_LOADDATA_OUT_PATH_SUFFIX
                )
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_load_data(
            uid=SBSPreprocessGenLoadDataModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(
            out_dir=data.storage_path.joinpath("index")
        )

        return SBSPreprocessGenLoadDataModule(spec=spec, pipe=pipe, uow=uow)
