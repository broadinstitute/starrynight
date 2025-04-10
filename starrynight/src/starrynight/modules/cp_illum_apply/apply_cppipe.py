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


def create_pipe_gen_cppipe(uid: str, spec: SpecContainer) -> Pipeline:
    """Create pipeline for generating cpipe.

    Parameters
    ----------
    uid: str
        Module unique id.
    spec: SpecContainer
        CPApplyIllumModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "illum",
        "apply",
        "cppipe",
        "-l",
        spec.inputs[0].path,
        "-o",
        spec.outputs[0].path,
        "-w",
        spec.inputs[1].path,
        "--nuclei",
        spec.inputs[2].path,
        "--cell",
        spec.inputs[3].path,
    ]

    gen_load_data_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={"load_data_path": [spec.inputs[0].path]},
                output_paths={"cppipe_path": [spec.outputs[0].path]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=cmd,
                    env={},
                ),
            ),
        ]
    )
    return gen_load_data_pipe


class CPApplyIllumGenCPPipeModule(StarrynightModule):
    """CP Apply illumination generate cppipe module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "cp_apply_illum_gen_cppipe"

    @staticmethod
    def _spec() -> str:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="load_data_path",
                    type=TypeEnum.files,
                    description="Path to the LoadData csv.",
                    optional=False,
                    path="path/to/the/loaddata",
                ),
                TypeInput(
                    name="workspace_path",
                    type=TypeEnum.file,
                    description="Workspace path.",
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
            ],
            outputs=[
                TypeOutput(
                    name="cp_apply_illum_cpipe",
                    type=TypeEnum.files,
                    description="Generated Illum calc cppipe files",
                    optional=False,
                    path="random/path/to/cppipe_dir",
                ),
                TypeOutput(
                    name="cppipe_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting cellprofiler pipeline files",
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
                        name="Starrynight CP illum apply generate cppipe module",
                        description="This module generates cppipe files for cp illumination correction apply module.",
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
            spec = CPApplyIllumGenCPPipeModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath(CP_ILLUM_APPLY_CP_LOADDATA_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.inputs[1].path = (
                data.workspace_path.joinpath(CP_ILLUM_APPLY_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.inputs[2].path = experiment.cp_config.nuclei_channel
            spec.inputs[3].path = experiment.cp_config.cell_channel

            spec.outputs[0].path = (
                data.workspace_path.joinpath(CP_ILLUM_APPLY_CP_CPPIPE_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_cppipe(
            uid=CPApplyIllumGenCPPipeModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return CPApplyIllumGenCPPipeModule(spec=spec, pipe=pipe, uow=uow)
