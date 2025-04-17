"""SBS Apply illumination correction calculate gen loaddata module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.experiments.pcp_generic import PCPGeneric
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_illum_apply.constants import (
    SBS_ILLUM_APPLY_CP_LOADDATA_OUT_PATH_SUFFIX,
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
                "inventory": [out_dir.joinpath("inventory.parquet").resolve().__str__()]
            },
            outputs={"index": [out_dir.joinpath("index.parquet").resolve().__str__()]},
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
        SBSApplyIllumModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "illum",
        "apply",
        "loaddata",
        "-i",
        spec.inputs[0].path,
        "-o",
        spec.outputs[0].path,
        "--nuclei",
        spec.inputs[1].path,
        "--sbs",
    ]
    # Use user provided parser if available
    if spec.inputs[2].path is not None:
        cmd += ["--path_mask", spec.inputs[1].path]
    gen_load_data_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={"index": [spec.inputs[0].path.__str__()]},
                output_paths={"load_data_path": [spec.outputs[0].path.__str__()]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=cmd,
                    env={},
                ),
            ),
        ]
    )
    return gen_load_data_pipe


class SBSApplyIllumGenLoadDataModule(StarrynightModule):
    """SBSApply illumination correction generate loaddata module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "sbs_apply_illum_gen_loaddata"

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
                    name="nuclei_channel",
                    type=TypeEnum.file,
                    description="Which channel to use for nuclei segmentation.",
                    optional=False,
                    path=None,
                ),
                TypeInput(
                    name="path_mask",
                    type=TypeEnum.file,
                    description="Path prefix mask to use.",
                    optional=True,
                    path=None,
                ),
            ],
            outputs=[
                TypeOutput(
                    name="sbs_apply_illum_loaddata",
                    type=TypeEnum.files,
                    description="Generated Illum calc loaddata files",
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
                        name="Starrynight SBS illum apply generate loaddata module",
                        description="This module generates load data files for sbs illumination apply module.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> "SBSApplyIllumGenLoadDataModule":
        """Create module from experiment and data config."""
        if spec is None:
            spec = SBSApplyIllumGenLoadDataModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath("index/index.parquet").resolve().__str__()
            )
            assert isinstance(experiment, PCPGeneric)
            spec.inputs[1].path = experiment.sbs_config.nuclei_channel
            spec.outputs[0].path = (
                data.workspace_path.joinpath(
                    SBS_ILLUM_APPLY_CP_LOADDATA_OUT_PATH_SUFFIX
                )
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_load_data(
            uid=SBSApplyIllumGenLoadDataModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return SBSApplyIllumGenLoadDataModule(spec=spec, pipe=pipe, uow=uow)
