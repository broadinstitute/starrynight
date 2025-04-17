"""CPCalculate illumination correction calculate invoke cellprofiler module."""
# pyright: reportCallIssue=false

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
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


def create_pipe_gen_cpinvoke(uid: str, spec: SpecContainer) -> Pipeline:
    """Create pipeline for invoking cellprofiler.

    Parameters
    ----------
    uid: str
        Module unique id.
    spec: SpecContainer
        CPCalcIllumInvokeCPModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "cp",
        "-p",
        spec.inputs[0].path,
        "-l",
        spec.inputs[1].path,
        "-o",
        spec.outputs[0].path,
    ]

    gen_load_data_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={
                    "cppipe_path": [
                        AnyPath(spec.inputs[0].path).parent.__str__()
                    ],
                    "load_data_path": [spec.inputs[1].path.__str__()],
                },
                output_paths={
                    "cp_illum_calc_dir": [spec.outputs[0].path.__str__()]
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


class CPCalcIllumInvokeCPModule(StarrynightModule):
    """CPCalculate illumination invoke cellprofiler module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "cp_calc_illum_invoke_cp"

    @staticmethod
    def _spec() -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="cppipe_path",
                    type=TypeEnum.files,
                    description="Path to the cppipe file.",
                    optional=False,
                    path="path/to/the/cppipe",
                ),
                TypeInput(
                    name="load_data_path",
                    type=TypeEnum.files,
                    description="Path to the LoadData csv.",
                    optional=False,
                    path="path/to/the/loaddata",
                ),
            ],
            outputs=[
                TypeOutput(
                    name="plate_illum",
                    type=TypeEnum.files,
                    description="Generated Illum correction files for the plate",
                    optional=False,
                    path="random/path/to/illum plate dir",
                ),
                TypeOutput(
                    name="cppipe_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting generated illum corrections",
                    optional=False,
                    path="http://karkinos:2720/?file=.%2FillumCPCalcOutput.py",
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
                        name="Starrynight CP illum calculation invoke cellprofiler module",
                        description="This module invoke cellprofiler for generating illumination corrections.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> "CPCalcIllumInvokeCPModule":
        """Create module from experiment and data config."""
        if spec is None:
            spec = CPCalcIllumInvokeCPModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath(
                    CP_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX,
                    CP_ILLUM_CALC_CP_CPPIPE_OUT_NAME,
                )
                .resolve()
                .__str__()
            )

            spec.inputs[1].path = (
                data.workspace_path.joinpath(
                    CP_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX
                )
                .resolve()
                .__str__()
            )

            spec.outputs[0].path = (
                data.workspace_path.joinpath(CP_ILLUM_CALC_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_cpinvoke(
            uid=CPCalcIllumInvokeCPModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(
            out_dir=data.storage_path.joinpath("index")
        )

        return CPCalcIllumInvokeCPModule(spec=spec, pipe=pipe, uow=uow)
