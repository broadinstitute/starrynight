"""CP segmentation check gen loaddata module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_apply.constants import CP_ILLUM_APPLY_OUT_PATH_SUFFIX
from starrynight.modules.cp_segcheck.constants import (
    CP_SEGCHECK_CP_LOADDATA_OUT_PATH_SUFFIX,
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
        CPPreSegcheckGenLoadDataModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "segcheck",
        "loaddata",
        "-i",
        spec.inputs[0].path,
        "-o",
        spec.outputs[0].path,
        "-c",
        spec.inputs[4].path,
        "--nuclei",
        spec.inputs[2].path,
        "--cell",
        spec.inputs[3].path,
    ]
    # Use user provided parser if available
    if spec.inputs[1].path is not None:
        cmd += ["--path_mask", spec.inputs[1].path]
    gen_load_data_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={"index": [spec.inputs[0].path]},
                output_paths={"load_data_path": [spec.outputs[0].path]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=cmd,
                    env={},
                ),
            ),
        ]
    )
    return gen_load_data_pipe


class CPSegcheckGenLoadDataModule(StarrynightModule):
    """CP segmentation generate loaddata module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "cp_segchek_gen_loaddata"

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
                    name="nuclei_channel",
                    type=TypeEnum.file,
                    description="Which channel to use for nuclei segmentation.",
                    optional=False,
                    path=None,
                ),
                TypeInput(
                    name="cell_channel",
                    type=TypeEnum.file,
                    description="Which channel to use for cell segmentation.",
                    optional=False,
                    path=None,
                ),
                TypeInput(
                    name="corr_images_path",
                    type=TypeEnum.file,
                    description="Path to corrected images.",
                    optional=False,
                    path="path/to/corr_images",
                ),
            ],
            outputs=[
                TypeOutput(
                    name="cp_segchek_loaddata",
                    type=TypeEnum.files,
                    description="Generated seg check loaddata files",
                    optional=False,
                    path="random/path/to/loaddata_dir",
                ),
                TypeOutput(
                    name="loaddata_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting load data files",
                    optional=False,
                    path="http://karkinos:2720/?file=.%2FillumCPApplyOutput.py",
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
                        name="Starrynight CP segmentation check generate loaddata module",
                        description="This module generates load data files for cp segcheck module.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> Self:
        """Create module from experiment and data config."""
        if spec is None:
            spec = CPSegcheckGenLoadDataModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath("index/index.parquet").resolve().__str__()
            )
            spec.inputs[2].path = experiment.cp_config.nuclei_channel
            spec.inputs[3].path = experiment.cp_config.cell_channel
            spec.inputs[4].path = (
                data.workspace_path.joinpath(CP_ILLUM_APPLY_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
            spec.outputs[0].path = (
                data.workspace_path.joinpath(CP_SEGCHECK_CP_LOADDATA_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_load_data(
            uid=CPSegcheckGenLoadDataModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return CPSegcheckGenLoadDataModule(spec=spec, pipe=pipe, uow=uow)
