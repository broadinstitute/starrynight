"""SBS Preprocess gen cpipe module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_preprocess.constants import (
    SBS_PREPROCESS_CP_CPPIPE_OUT_PATH_SUFFIX,
    SBS_PREPROCESS_CP_LOADDATA_OUT_PATH_SUFFIX,
    SBS_PREPROCESS_OUT_PATH_SUFFIX,
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
        SBPreprocessModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "preprocess",
        "cppipe",
        "-l",
        spec.inputs[0].path,
        "-o",
        spec.outputs[0].path,
        "-w",
        spec.inputs[1].path,
        "-b",
        spec.inputs[2].path,
        "-n",
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


class SBSPreprocessGenCPPipeModule(StarrynightModule):
    """SBS preprocess cppipe module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "sbs_preprocess_gen_cppipe"

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
                    name="barcode_path",
                    type=TypeEnum.file,
                    description="Path to barcode csv.",
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
                    name="sbs_preprocess_cpipe",
                    type=TypeEnum.files,
                    description="Generated sbs preprocess cppipe files",
                    optional=False,
                    path="random/path/to/cppipe_dir",
                ),
                TypeOutput(
                    name="cppipe_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting cellprofiler pipeline files",
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
                        name="Starrynight SBS preprocess generate cppipe module",
                        description="This module generates cppipe files for sbs preprocess module.",
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
            spec = SBSPreprocessGenCPPipeModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath(SBS_PREPROCESS_CP_LOADDATA_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.inputs[1].path = (
                data.workspace_path.joinpath(SBS_PREPROCESS_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
            spec.inputs[2].path = "changeme"
            spec.inputs[3].path = "changeme"

            spec.outputs[0].path = (
                data.workspace_path.joinpath(SBS_PREPROCESS_CP_CPPIPE_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_cppipe(
            uid=SBSPreprocessGenCPPipeModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return SBSPreprocessGenCPPipeModule(spec=spec, pipe=pipe, uow=uow)
