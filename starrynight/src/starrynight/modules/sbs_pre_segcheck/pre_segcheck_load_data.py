"""CP pre segmentation check gen loaddata module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_pre_segcheck.constants import (
    SBS_PRE_SEGCHECK_CP_LOADDATA_OUT_PATH_SUFFIX,
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
        SBSPreSegcheckGenLoadDataModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "presegcheck",
        "loaddata",
        "-i",
        spec.inputs[0].path,
        "-o",
        Path(spec.outputs[0].path).resolve().__str__(),
        "--sbs",
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


class SBSPreSegcheckGenLoadDataModule(StarrynightModule):
    """SBS pre segmentation generate loaddata module."""

    @staticmethod
    def module_name() -> str:
        """Return module name."""
        return "sbs_pre_segchek_gen_loaddata"

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "sbs_pre_segchek_gen_loaddata"

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
            ],
            outputs=[
                TypeOutput(
                    name="sbs_pre_segchek_loaddata",
                    type=TypeEnum.files,
                    description="Generated pre seg check loaddata files",
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
                        name="Starrynight SBS pre-segmentation check generate loaddata module",
                        description="This module generates load data files for sbs pre segcheck module.",
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
            spec = SBSPreSegcheckGenLoadDataModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath("index/index.parquet")
                .resolve()
                .__str__()
            )
            spec.outputs[0].path = (
                data.workspace_path.joinpath(
                    SBS_PRE_SEGCHECK_CP_LOADDATA_OUT_PATH_SUFFIX
                )
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_load_data(
            uid=SBSPreSegcheckGenLoadDataModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(
            out_dir=data.storage_path.joinpath("index")
        )

        return SBSPreSegcheckGenLoadDataModule(spec=spec, pipe=pipe, uow=uow)
